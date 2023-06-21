odoo.define('dashboard_pos.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
const { loadBundle } = require("@web/core/assets");
var ajax = require('web.ajax');
var session = require('web.session');
var web_client = require('web.web_client');
var rpc = require('web.rpc');
var _t = core._t;
var QWeb = core.qweb;

var PosDashboard = AbstractAction.extend({
    template: 'AccountDashboard',
    events: {
        //'click .pos_refund_orders':'pos_refund_orders',
        //'click .pos_refund_today_orders':'pos_refund_today_orders',
        "click .o_change_period": "change_dashboard",
        //'change #pos_sales': 'onclick_pos_sales',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['PosCustomer'];
        this.payment_details = [];
        this.top_salesperson = [];
        this.selling_product = [];
        this.stock_value = [];
    },

    willStart: function() {
        var self = this;

        var cookie = self.get_cookie();
            if (self.get_used_date() === "1") {
                self.set_cookie("", "");
                self.set_used_date("0");
            }

        return $.when(loadBundle(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        var la_data = self.get_cookie();
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');

            // Manipulation des donnees du cookie
                // Les lignes de codes suivantes servent a définir l'état des dates contenues dans la cookie
                // Si elles ont deja ete utilisées pour afficher les résultats voulus ou pas
                var cookies = document.cookie.split(";");
                var temp = 0;
                var c = 0;

                for (var i = 0; i < cookies.length; i++) {
                    if (cookies[i].includes("compteur")) {
                        if (la_data["start_date"] !== "") {
                            temp = 1;
                            var c = parseInt(cookies[i].split("=")[1]);
                            c += 1;
                            document.cookie = "compteur=" + c;
                            console.log("Compteur get_cookie increment :", c);
                        }
                    } else {
                        if (i === cookies.length - 1 && temp === 0) {
                            document.cookie = "compteur=" + 0;
                            console.log("Compteur get_cookie cree");
                        }
                    }
                }
                // Lorsque 0<c<1, la date n'a pas encore ete utilisée
                if (c > 1) {
                    self.set_used_date("1");
                    document.cookie = "compteur=" + 0;
                    console.log("Compteur cookie réinitialisé");
                }

        });
    },

    fetch_data: function() {
        var self = this;
        var la_data = self.get_cookie();
        // var def1 =  this._rpc({
        //         model: 'pos.order',
        //         method: 'get_refund_details'
        // }).then(function(result) {
        //    self.total_sale = result['total_sale'],
        //    self.total_order_count = result['total_order_count']
        //    self.total_refund_count = result['total_refund_count']
        //    self.total_session = result['total_session']
        //    self.today_refund_total = result['today_refund_total']
        //    self.today_sale = result['today_sale']
        // });
      var state = true
      var search_data = {'is_search': false, 'start_date': la_data["start_date"], 'end_date': la_data["end_date"]};

      if (la_data["start_date"] === "") {
          console.log('search data ........ first ........', search_data);
          var def2 = self._rpc({
                model: "mini.account.dashboard",
                method: "get_information",
                args : [state, search_data],
            });

      }
      else{
          search_data['is_search'] = true;
          var def2 = self._rpc({
                model: "mini.account.dashboard",
                method: "get_information",
                args : [state, search_data],
            });
          console.log('search data ........ 222 ........', search_data);
      }
      def2.then(function (res) {
          self.payment_details = res['customer_data'];
          self.top_salesperson = res['cash_data'];
          self.selling_product = res['vendor_data'];

          if (la_data["start_date"] !== "") {
              self.default_start_date = la_data["start_date"];
              self.default_end_date = la_data["end_date"];
          }
      });

        return $.when(def2);
    },

    render_dashboards: function() {
        var self = this;
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_pos_dashboard').append(QWeb.render(template, {widget: self}));
            });
    },
    render_graphs: function(){
        var self = this;
//        self.render_top_customer_graph();
         //self.render_product_category_graph();
    },

    pos_order_today: function(e){
        var self = this;
        var date = new Date();
        var yesterday = new Date(date.getTime());
        yesterday.setDate(date.getDate() - 1);
        e.stopPropagation();
        e.preventDefault();

        session.user_has_group('hr.group_hr_user').then(function(has_group){
            if(has_group){
                var options = {
                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                };
                self.do_action({
                    name: _t("Today Order"),
                    type: 'ir.actions.act_window',
                    res_model: 'pos.order',
                    view_mode: 'tree,form,calendar',
                    view_type: 'form',
                    views: [[false, 'list'],[false, 'form']],
                    domain: [['date_order','<=', date],['date_order', '>=', yesterday]],
                    target: 'current'
                }, options)
            }
        });

    },

    change_dashboard: function () {
        location.reload();
        var self = this;
        self.set_used_date("0");
        self.recuperate_date();
        self.willStart();
        // self.start();
        window.unload = function () {
            self.set_cookie("", "");
            console.log("Unload ici");
            self.set_used_date(1);
            return "yo";
        };
    },

    //  fonction de Récupération de la date passer par le formulaire
    recuperate_date: function () {

        var date_start =
            $("#start_date").val() == ""
                ? new Date()
                : new Date($("#start_date").val());

        var date_end =
            $("#end_date").val() == ""
                ? new Date()
                : new Date($("#end_date").val());

        if (date_end < date_start) {
            alert("La date de fin doit être supérieur à celle du début !")
        }
        else {
            var day = date_start.getDate();
            var month = date_start.getMonth() + 1;
            if (month < 10) {
                month = "0" + month;
            }
            if (day < 10) {
                day = "0" + day;
            }
            var year = date_start.getFullYear();

            if (year !== "NaN" && month !== "NaN" && day !== "NaN")
                var start_date = [day, month, year].join("/");
            else var start_date = "";

            var date_end =
                $("#end_date").val() == ""
                    ? new Date()
                    : new Date($("#end_date").val());
            var day = date_end.getDate();
            var month = date_end.getMonth() + 1;
            if (month < 10) {
                month = "0" + month;
            }
            if (day < 10) {
                day = "0" + day;
            }
            var year = date_end.getFullYear();

            if (year !== "NaN" && month !== "NaN" && day !== "NaN")
                var end_date = [day, month, year].join("/");
            else var end_date = "";

            if (start_date !== "NaN-NaN-NaN" && end_date !== "NaN-NaN-NaN") {
                this.set_cookie(start_date, end_date);
            } else {
                this.set_cookie("", "");
            }
        }
    },
    //  Sauvegarde des dates dans le cookie
    set_cookie: function (start_date, end_date) {
        document.cookie = "start_date=" + start_date;
        document.cookie = "end_date=" + end_date;
    },
    //  Récupération des dates contenues dans le cookie
    get_cookie: function () {
        var cookies = document.cookie.split(";");
        var start_date = "";
        var end_date = "";
        for (var i = 0; i < cookies.length; i++) {
            if (cookies[i].includes("start_date"))
                start_date = cookies[i].split("=")[1];
            if (cookies[i].includes("end_date"))
                end_date = cookies[i].split("=")[1];
        }
        if (this.get_used_date() === "1") {
            start_date = "";
            end_date = "";
        }
        var la_data = { start_date: start_date, end_date: end_date };
        return la_data;
    },
    //  Fonction permettant de définir lorsqu'une date a ete deja utilise ou pas
    set_used_date: function (val) {
        document.cookie = "used=" + val;
    },
    //  Récupérer l'état d'utilisation des dates
    get_used_date: function () {
        var cookies = document.cookie.split(";");
        var is_used = "0";
        for (var i = 0; i < cookies.length; i++) {
            if (cookies[i].includes("used")) is_used = cookies[i].split("=")[1];
        }
        return is_used;
    },


});


core.action_registry.add('account_dashboard', PosDashboard);

return PosDashboard;

});
