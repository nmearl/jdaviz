<template>
  <component :is="stack.container">
    <g-viewer-tab
      v-for="(child, index) in stack.children"
      :stack="child"
      :key="index"
      :data-items="dataItems"
      :dragging="dragging"
      @resize="$emit('resize')"
      @destroy="$emit('destroy', $event)"
      @data-item-selected="$emit('data-item-selected', $event)"
    ></g-viewer-tab>
    <gl-component
      v-for="(viewer, index) in stack.viewers"
      :key="index"
      title="Test"
      :tab-id="viewer.id"
      @resize="$emit('resize')"
      @destroy="$emit('destroy', viewer.id)"
    >
      <draggable :group="{name:'data'}" @add="onDataAdded" class="drop-target">
        <v-overlay absolute :value="dragging">
          <p>Drop data to plot {{ dragging }}</p>
        </v-overlay>
      </draggable>
      <v-toolbar dense height="32px" flat color="#e2e4e8">
        <!-- <v-sheet class="fill-height d-flex pa-2" style="flex-direction: column"> -->
        <v-btn tile outlined small class="mx-1">
          <v-icon>mdi-magnify</v-icon>
        </v-btn>

        <v-btn tile outlined small class="mx-1">
          <v-icon>mdi-heart</v-icon>
        </v-btn>

        <v-btn tile outlined small class="mx-1">
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>

        <v-btn tile outlined small class="mx-1">
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>

        <v-btn tile outlined small class="mx-1">
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
        <!-- </v-sheet> -->
      </v-toolbar>
      <!-- <v-card tile flat style="height: calc(100% - 2px); margin-top: -2px;"> -->
      <!-- <v-navigation-drawer permanent mini-variant absolute>
          <v-list nav dense>
            <v-list-item link>
              <v-list-item-icon>
                <v-icon>mdi-folder</v-icon>
              </v-list-item-icon>
              <v-list-item-title>My Files</v-list-item-title>
            </v-list-item>
            <v-list-item link>
              <v-list-item-icon>
                <v-icon>mdi-account-multiple</v-icon>
              </v-list-item-icon>
              <v-list-item-title>Shared with me</v-list-item-title>
            </v-list-item>
            <v-list-item link>
              <v-list-item-icon>
                <v-icon>mdi-star</v-icon>
              </v-list-item-icon>
              <v-list-item-title>Starred</v-list-item-title>
            </v-list-item>
          </v-list>
      </v-navigation-drawer>-->
      <!-- <v-toolbar dense absolute dark>
          <v-toolbar-items>
            <jupyter-widget :widget="viewer.tools"></jupyter-widget>
            <v-menu offset-y :close-on-content-click="false" style="z-index: 10">
              <template v-slot:activator="{ on }">
                <v-btn icon color="primary" v-on="on">
                  <v-icon>mdi-settings</v-icon>
                </v-btn>
              </template>

              <v-tabs v-model="viewer.tab" grow height="36px">
                <v-tab key="0">Data</v-tab>
                <v-tab key="1">Layer</v-tab>
                <v-tab key="2">Viewer</v-tab>
              </v-tabs>

              <v-tabs-items v-model="viewer.tab" style="max-height: 500px; width: 350px;">
                <v-tab-item key="0" class="overflow-y-auto" style="height: 450px">
                  <v-treeview
                    dense
                    selectable
                    :items="dataItems"
                    hoverable
                    v-model="viewer.selected_data_items"
                    activatable
                    item-disabled="locked"
                    @input="$emit('data-item-selected', {'id': viewer.id, 'selected_items': $event})"
                  ></v-treeview>
                </v-tab-item>

                <v-tab-item key="1" eager class="overflow-y-auto" style="height: 100%">
                  <v-sheet class="px-4">
                    <jupyter-widget :widget="viewer.layer_options" />
                  </v-sheet>
                </v-tab-item>

                <v-tab-item key="2" eager class="overflow-y-auto" style="height: 100%">
                  <v-sheet class="px-4">
                    <jupyter-widget :widget="viewer.viewer_options" />
                  </v-sheet>
                </v-tab-item>
              </v-tabs-items>
            </v-menu>
          </v-toolbar-items>
      </v-toolbar>-->
      <!-- <v-container class="fill-height pa-0 ma-0"> -->
      <jupyter-widget :widget="viewer.widget" style="width: 100%; height: calc(100% - 52px)" />
      <!-- </v-container> -->
      <!-- </v-card> -->
    </gl-component>
  </component>
</template>

<script>
module.exports = {
  name: "g-viewer-tab",
  props: ["stack", "dataItems", "dragging"],
  data() {
    return { hiddenList: [] };
  },
  created() {
    this.$parent.childMe = () => {
      return this.$children[0];
    };
  },
  methods: {
    computeChildrenPath() {
      return this.$parent.computeChildrenPath();
    },
    onDataAdded(e) {
      console.log("Data added");
    }
  },
  computed: {
    parentMe() {
      return this.$parent;
    },
    childMe() {
      return this.$children[0];
    }
  }
};
</script>

<style>
/* Hide dragged element in target */
.drop-target > [draggable="true"] {
  display: none;
}
</style>