import os
import pickle

import astropy.modeling.models as models
import astropy.units as u
from glue.core.message import (SubsetCreateMessage,
                               SubsetDeleteMessage,
                               SubsetUpdateMessage)
from traitlets import Bool, Int, List, Unicode

from jdaviz.core.events import AddDataMessage, RemoveDataMessage
from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import TemplateMixin
from jdaviz.utils import load_template
from .fitting_backend import fit_model_to_spectrum
from .initializers import initialize, model_parameters

__all__ = ['ModelFitting']

MODELS = {
     'Const1D': models.Const1D,
     'Linear1D': models.Linear1D,
     'Polynomial1D': models.Polynomial1D,
     'Gaussian1D': models.Gaussian1D,
     'Voigt1D': models.Voigt1D,
     'Lorentz1D': models.Lorentz1D
     }


@tray_registry('g-model-fitting', label="Model Fitting")
class ModelFitting(TemplateMixin):
    dialog = Bool(False).tag(sync=True)
    template = load_template("model_fitting.vue", __file__).tag(sync=True)
    dc_items = List([]).tag(sync=True)

    save_enabled = Bool(False).tag(sync=True)
    model_label = Unicode().tag(sync=True)
    model_save_path = Unicode().tag(sync=True)
    temp_name = Unicode().tag(sync=True)
    temp_model = Unicode().tag(sync=True)
    model_equation = Unicode().tag(sync=True)
    eq_error = Bool(False).tag(sync=True)
    component_models = List([]).tag(sync=True)
    display_order = Bool(False).tag(sync=True)
    poly_order = Int(0).tag(sync=True)

    available_models = List(list(MODELS.keys())).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._viewer_spectra = None
        self._spectrum1d = None
        self._units = {}
        self.n_models = 0
        self._fitted_model = None
        self._fitted_spectrum = None
        self.component_models = []
        self._initialized_models = {}
        self._display_order = False
        self.model_save_path = os.getcwd()
        self.model_label = "Model"

        self.hub.subscribe(self, AddDataMessage,
                           handler=self._on_viewer_data_changed)

        self.hub.subscribe(self, RemoveDataMessage,
                           handler=self._on_viewer_data_changed)

        self.hub.subscribe(self, SubsetCreateMessage,
                           handler=lambda x: self._on_viewer_data_changed())

        self.hub.subscribe(self, SubsetDeleteMessage,
                           handler=lambda x: self._on_viewer_data_changed())

        self.hub.subscribe(self, SubsetUpdateMessage,
                           handler=lambda x: self._on_viewer_data_changed())

    def _on_viewer_data_changed(self, msg=None):
        """
        Callback method for when data is added or removed from a viewer, or
        when a subset is created, deleted, or updated. This method receieves
        a glue message containing viewer information in the case of the former
        set of events, and updates the available data list displayed to the
        user.

        Notes
        -----
        We do not attempt to parse any data at this point, at it can cause
        visible lag in the application.

        Parameters
        ----------
        msg : `glue.core.Message`
            The glue message passed to this callback method.
        """
        self._viewer_id = self.app._viewer_item_by_reference(
            'spectrum-viewer').get('id')

        # Subsets are global and are not linked to specific viewer instances,
        # so it's not required that we match any specific ids for that case.
        # However, if the msg is not none, check to make sure that it's the
        # viewer we care about.
        if msg is not None and msg.viewer_id != self._viewer_id:
            return

        viewer = self.app.get_viewer('spectrum-viewer')

        self.dc_items = [layer_state.layer.label
                         for layer_state in viewer.state.layers]

    def _param_units(self, param, order = 0):
        """Helper function to handle units that depend on x and y"""
        y_params = ["amplitude", "amplitude_L", "intercept"]

        if param == "slope":
            return str(u.Unit(self._units["y"]) / u.Unit(self._units["x"]))
        elif param == "poly":
            return str(u.Unit(self._units["y"]) / u.Unit(self._units["x"])**order)

        return self._units["y"] if param in y_params else self._units["x"]

    def _update_parameters_from_fit(self):
        """Insert the results of the model fit into the component_models"""
        for m in self.component_models:
            name = m["id"]
            if len(self.component_models) > 1:
                m_fit = self._fitted_model.unitless_model[name]
            else:
                m_fit = self._fitted_model
            temp_params = []
            for i in range(0, len(m_fit.parameters)):
                temp_param = [x for x in m["parameters"] if x["name"] ==
                              m_fit.param_names[i]]
                temp_param[0]["value"] = m_fit.parameters[i]
                temp_params += temp_param
            m["parameters"] = temp_params
        # Trick traitlets into updating the displayed values
        component_models = self.component_models
        self.component_models = []
        self.component_models = component_models

    def _update_initialized_parameters(self):
        # If the user changes a parameter value, we need to change it in the
        # initialized model
        for m in self.component_models:
            name = m["id"]
            for param in m["parameters"]:
                quant_param = u.Quantity(param["value"], param["unit"])
                setattr(self._initialized_models[name], param["name"],
                        quant_param)

    def vue_data_selected(self, event):
        """
        Callback method for when the user has selected data from the drop down
        in the front-end. It is here that we actually parse and create a new
        data object from the selected data. From this data object, unit
        information is scraped, and the selected spectrum is stored for later
        use in fitting.

        Parameters
        ----------
        event : str
            IPyWidget callback event object. In this case, represents the data
            label of the data collection object selected by the user.
        """
        selected_spec = self.app.get_data_from_viewer("spectrum-viewer",
                                                      data_label=event)[event]

        if self._units == {}:
            self._units["x"] = str(
                selected_spec.spectral_axis.unit)
            self._units["y"] = str(
                selected_spec.flux.unit)

        self._spectrum1d = selected_spec

    def vue_model_selected(self, event):
        # Add the model selected to the list of models
        self.temp_model = event
        if event == "Polynomial1D":
            self.display_order = True
        else:
            self.display_order = False

    def _initialize_polynomial(self, new_model):
        initialized_model = initialize(
            MODELS[self.temp_model](name=self.temp_name, degree=self.poly_order),
            self._spectrum1d.spectral_axis,
            self._spectrum1d.flux)

        self._initialized_models[self.temp_name] = initialized_model

        for i in range(self.poly_order + 1):
            param = "c{}".format(i)
            initial_val = getattr(initialized_model, param).value
            new_model["parameters"].append({"name": param,
                                            "value": initial_val,
                                            "unit": self._param_units("poly", i),
                                            "fixed": False})
        return new_model

    def vue_add_model(self, event):
        """Add the selected model and input string ID to the list of models"""
        new_model = {"id": self.temp_name, "model_type": self.temp_model,
                     "parameters": []}

        # Need to do things differently for polynomials, since the order varies
        if self.temp_model == "Polynomial1D":
            new_model = self._initialize_polynomial(new_model)
        else:
            # Have a separate private dict with the initialized models, since
            # they don't play well with JSON for widget interaction
            initialized_model = initialize(
                MODELS[self.temp_model](name=self.temp_name),
                self._spectrum1d.spectral_axis,
                self._spectrum1d.flux)

            self._initialized_models[self.temp_name] = initialized_model

            for param in model_parameters[new_model["model_type"]]:
                initial_val = getattr(initialized_model, param).value
                new_model["parameters"].append({"name": param,
                                                "value": initial_val,
                                                "unit": self._param_units(param),
                                                "fixed": False})

        new_model["Initialized"] = True
        self.component_models = self.component_models + [new_model]

    def vue_remove_model(self, event):
        self.component_models = [x for x in self.component_models
                                 if x["id"] != event]
        del(self._initialized_models[event])

    def vue_save_model(self, event):
        if self.model_save_path[-1] == "/":
            connector = ""
        else:
            connector = "/"
        full_path = self.model_save_path + connector + self.model_label + ".pkl"
        with open(full_path, 'wb') as f:
            pickle.dump(self._fitted_model, f)

    def vue_equation_changed(self, event):
        # Length is a dummy check to test the infrastructure
        if len(self.model_equation) > 20:
            self.eq_error = True

    def vue_model_fitting(self, *args, **kwargs):
        """
        Run fitting on the initialized models, fixing any parameters marked
        as such by the user, then update the displauyed parameters with fit
        values
        """
        fitted_model, fitted_spectrum = fit_model_to_spectrum(
            self._spectrum1d,
            self._initialized_models.values(),
            self.model_equation,
            run_fitter=True)
        self._fitted_model = fitted_model
        self._fitted_spectrum = fitted_spectrum

        # Update component model parameters with fitted values
        self._update_parameters_from_fit()

        self.save_enabled = True

    def vue_register_spectrum(self, event):
        """
        Add a spectrum to the data collection based on the currently displayed
        parameters (these could be user input or fit values).
        """
        # Make sure the initialized models are updated with any user-specified
        # parameters
        self._update_initialized_parameters()

        # Need to run the model fitter with run_fitter=False to get spectrum
        model, spectrum = fit_model_to_spectrum(self._spectrum1d,
                                                self._initialized_models.values(),
                                                self.model_equation)

        self.n_models += 1
        label = self.model_label
        if label in self.data_collection:
            self.app.remove_data_from_viewer('spectrum-viewer', label)
            # Some hacky code to remove the label from the data dropdown
            temp_items = []
            for data_item in self.app.state.data_items:
                if data_item['name'] != label:
                    temp_items.append(data_item)
            self.app.state.data_items = temp_items
            # Remove the actual Glue data object from the data_collection
            self.data_collection.remove(self.data_collection[label])
        self.data_collection[label] = spectrum
        self.save_enabled = True

        #sleep(1)
        #self.app.add_data_to_viewer('spectrum-viewer', label)
