<template>
  <v-app id="web-app">
    <v-app-bar dark dense flat app absolute clipped-right clipped-left>
      <jupyter-widget :widget="item.widget" v-for="item in state.tool_items" :key="item.name"></jupyter-widget>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-btn icon @click="state.plugin_drawer = !state.plugin_drawer">
          <v-icon v-if="state.plugin_drawer">mdi-toy-brick-remove</v-icon>
          <v-icon v-else>mdi-toy-brick-plus</v-icon>
        </v-btn>
        <v-btn icon @click="state.data_drawer = !state.data_drawer">
          <v-icon v-if="state.data_drawer">mdi-toy-brick-remove</v-icon>
          <v-icon v-else>mdi-toy-brick-plus</v-icon>
        </v-btn>
      </v-toolbar-items>
    </v-app-bar>

    <v-content
      :style="checkNotebookContext() ? 'height: ' + state.settings.context.notebook.max_height + '; border: solid 1px #e5e5e5;' : ''"
    >
      <v-container class="fill-height pa-0" fluid>
        <v-row class="fill-height pa-0 ma-0">
          <v-col class="fill-height pa-0 ma-0">
            <!-- :style="checkNotebookContext() ? 'height: 100%;' : 'height: calc(100vh - 48px)'" -->
            <splitpanes>
              <pane v-if="state.data_drawer">
                <v-card flat tile color="#f8f8f8">
                  <v-list dense class="overflow-y-auto fill-height">
                    <draggable
                      v-model="state.data_items"
                      :group="{name:'data', pull:'clone'}"
                      style="min-height: 10px"
                      @start="onDataDragged('start')"
                      @end="onDataDragged('end')"
                    >
                      <template v-for="(data, i) in state.data_items">
                        <v-list-group prepend-icon="account_circle" value="true" :key="i">
                          <template v-slot:activator>
                            <v-list-item-title>{{ data.name }}</v-list-item-title>
                          </template>
                          <v-list-item v-for="(child, i) in data.children" :key="i">
                            <v-list-item-title v-text="child.name"></v-list-item-title>
                            <!--                        <v-list-item-icon>-->
                            <!--                          <v-icon v-text="admin[1]"></v-icon>-->
                            <!--                        </v-list-item-icon>-->
                          </v-list-item>
                        </v-list-group>
                      </template>
                    </draggable>
                  </v-list>
                  <v-divider></v-divider>
                </v-card>
              </pane>
              <pane>
                <splitpanes>
                  <pane>
                    <golden-layout
                      :has-headers="state.settings.visible.tab_headers"
                      style="height: 100%"
                    >
                      <gl-row :closable="false">
                        <g-viewer-tab
                          v-for="(stack, index) in state.stack_items"
                          :stack="stack"
                          :key="index"
                          :data-items="state.data_items"
                          :dragging="state.dragging_data"
                          @resize="relayout"
                          @destroy="destroy_viewer_item($event)"
                          @data-item-selected="data_item_selected($event)"
                        ></g-viewer-tab>
                      </gl-row>
                    </golden-layout>
                  </pane>
                </splitpanes>
              </pane>
              <pane v-if="state.plugin_drawer">
                <v-card flat tile class="overflow-y-auto fill-height" color="#f8f8f8">
                  <v-expansion-panels accordion multiple focusable flat tile>
                    <v-expansion-panel v-for="(tray, index) in state.tray_items" :key="index">
                      <v-expansion-panel-header>{{ tray.label }}</v-expansion-panel-header>
                      <v-expansion-panel-content>
                        <jupyter-widget :widget="tray.widget"></jupyter-widget>
                      </v-expansion-panel-content>
                    </v-expansion-panel>
                  </v-expansion-panels>
                  <v-divider></v-divider>
                </v-card>
              </pane>
            </splitpanes>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
    <v-snackbar
      v-model="state.snackbar.show"
      :timeout="state.snackbar.timeout"
      :color="state.snackbar.color"
      absolute
    >
      {{ state.snackbar.text }}
      <v-btn text @click="state.snackbar.show = false">Close</v-btn>
    </v-snackbar>
  </v-app>
</template>

<script>
export default {
  methods: {
    checkNotebookContext() {
      this.notebook_context = document.getElementById("ipython-main-app");
      return this.notebook_context;
    },
    onDataDragged(e) {
      this.on_data_dragged(e)
    }
  }
};
</script>

<style id="web-app">
.v-btn:not(.v-btn--round).v-size--small {
  min-width: 28px;
  padding: 0px;
}

.v-toolbar__content,
.vuetify-styles .v-toolbar__content {
  padding-left: 0px;
  padding-right: 0px;
}

.v-tabs-items {
  height: 100%;
}

.splitpanes {
  background-color: #f8f8f8;
}

.splitpanes__splitter {
  background-color: #e2e4e8;
  position: relative;
  width: 5px;
}

.lm_goldenlayout {
  background: #f8f8f8;
}

.lm_content {
  background: #ffffff;
  border: none;
  /*border-top: 1px solid #cccccc;*/
}

.lm_splitter {
  background: #e2e4e8;
  opacity: 1;
  z-index: 1;
}

/* .lm_splitter.lm_vertical {
  height: 1px !important;
}

.lm_splitter.lm_horizontal {
  width: 1px !important;
} */

.lm_header .lm_tab {
  padding-top: 0px;
  margin-top: 0px;
}

.vuetify-styles .lm_header ul {
  padding-left: 0;
}

.v-expansion-panel-content__wrap {
  padding: 0px;
  margin: 0px;
}

.v-expansion-panel__header {
  padding: 0px;
  margin: 0px;
}

.vuetify-styles .v-expansion-panel-content__wrap {
  padding: 0px;
  margin: 0px;
}
</style>
