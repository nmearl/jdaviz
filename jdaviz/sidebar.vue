<template>
  <v-navigation-drawer
    ref="drawer"
    app
    clipped
    absolute
    :right="right"
    :width="navigation.width"
    v-model="visible"
    :style="right ? 'padding-left: 5px' : 'padding-right: 5px'"
  >
    <slot></slot>
  </v-navigation-drawer>
</template>

<script>
module.exports = {
  name: "g-sidebar",
  props: ["visible", "right"],
  data: () => {
    return {
      navigation: {
        shown: true,
        width: 350,
        borderSize: 5
      }
    };
  },
  computed: {
    direction() {
      return this.visible === false ? "Open" : "Closed";
    }
  },
  methods: {
    setBorderWidth() {
      let i = this.$refs.drawer.$el.querySelector(
        ".v-navigation-drawer__border"
      );
      i.style.width = this.navigation.borderSize + "px";
      i.style.cursor = "ew-resize";
    },
    setEvents() {
      const minSize = this.navigation.borderSize;
      const el = this.$refs.drawer.$el;
      const drawerBorder = el.querySelector(".v-navigation-drawer__border");
      const vm = this;
      const direction = el.classList.contains("v-navigation-drawer--right")
        ? "right"
        : "left";

      function resize(e) {
        document.body.style.cursor = "ew-resize";
        let f =
          direction === "right"
            ? document.body.scrollWidth - e.clientX
            : e.clientX;
        el.style.width = f + "px";
      }

      drawerBorder.addEventListener(
        "mousedown",
        function(e) {
          if (e.button != 0) return;

          if (e.offsetX < minSize) {
            m_pos = e.x;
            el.style.transition = "initial";
            document.addEventListener("mousemove", resize, false);
          }
        },
        false
      );

      document.addEventListener(
        "mouseup",
        function() {
          el.style.transition = "";
          vm.navigation.width = el.style.width;
          document.body.style.cursor = "";
          document.removeEventListener("mousemove", resize, false);
        },
        false
      );
    }
  },
  mounted() {
    this.setBorderWidth();
    this.setEvents();
  }
};
</script>
