odoo.define("dashboard_ro.Dashboard", function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    const { loadBundle } = require("@web/core/assets");
    var ajax = require("web.ajax");
    var session = require("web.session");
    var web_client = require("web.web_client");
    var rpc = require("web.rpc");
    var _t = core._t;
    var QWeb = core.qweb;

    var RoDashboard = AbstractAction.extend({
        template: "RoDashboard",
        events: {
            "click .pos_order_today": "pos_order_today",
            "click .pos_order": "pos_order",
            "click .pos_total_sales": "pos_order",
            "click .pos_session": "pos_session",
            "click .pos_refund_orders": "pos_refund_orders",
            "click .pos_refund_today_orders": "pos_refund_today_orders",
            "click .o_change_period": "change_dashboard",
            "change #ros_sales": "onclick_ros_sales",
            "change #ros_sales_compta": "onclick_ros_sales_compta",
        },

        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ["RoTotal", "RoChart", "RoDetails"];
            this.total_entree = [];
            this.entree_mecha = [];
            this.entree_carrosserie = [];
            this.entree_painting = [];
            this.total_cac = [];
            this.ca_ht = [];
            this.ca_ttc = [];
            this.ca_cp = [];
            this.ca_cnp = [];
            this.ca_nc = [];
            this.cac_mecha = [];
            this.cac_carrosserie = [];
            this.cac_painting = [];
            this.cac_autre = [];
            this.entree_autre = [];
            this.default_start_date = "";
            this.default_end_date = "";
            this.customer_data = [];
            this.vendor_data = [];
            this.cash_data = [];
        },

        // La 1ere fonction exécutée
        willStart: function () {
            var self = this;
            //  Récupération des dates dans le cookie
            var cookie = self.get_cookie();
            if (self.get_used_date() === "1") {
                self.set_cookie("", "");
                self.set_used_date("0");
            }
            // Récupération des informations depuis le model
            return $.when(loadBundle(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },

        // La 2eme fonction exécutée
        start: function () {
            var self = this;
            var la_data = self.get_cookie();
            this.set("title", "Dashboard");

            return this._super().then(function () {
                self.render_dashboards();
                self.render_graphs();
                self.$el.parent().addClass("oe_background_grey");

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

        // Permet de définir les données à afficher dans les différentes section de ro_dashboard
        fetch_data: function () {
            var self = this;
            var la_data = self.get_cookie();
            var params = window.location.href.split("&");
            var len = params.length;
            var i = 0;
            for (i = 0; i < len; i++) {
                if (params[i].includes("cids")) {
                    var current_cid = params[i].split("=")[1];
                    if (current_cid.length > 2) {
                        current_cid = 0;
                    }
                    break;
                }
            }
            // Si une période n'est pas choisie, on fait un affichage apr défaut
            if (la_data["start_date"] === "") {
                var def1 = this._rpc({
                    model: "mini.account.dashboard",
                    method: "get_information",
                });
            }
            // sion, on tien compte de la valeur de la_data et on la passe en paramètre de get_repair_order_details
            else {
                var def1 = this._rpc({
                    model: "mini.account.dashboard",
                    method: "get_information",
                    args: [la_data],
                });
            }
            def1.then(function (result) {
                // Les variables retournées dans le fichier ro_dashboard.py sont utilisables dans le fichier ro_dashboard.xml
                // affichées dans la section 2
                self.total_entree = result["total_entree"];
                self.entree_mecha = result["entree_mecha"];
                self.entree_carrosserie = result["entree_carrosserie"];
                self.entree_painting = result["entree_painting"];
                self.ca_ht = result["ca_ht"];
                self.ca_ttc = result["ca_ttc"];
                self.ca_cnp = result["ca_cnp"];
                self.ca_nc = result["ca_nc"];
                self.ca_cp = result["ca_cp"];
                self.total_cac = result["total_cac"];
                self.cac_mecha = result["cac_mecha"];
                self.cac_carrosserie = result["cac_carrosserie"];
                self.cac_painting = result["cac_painting"];
                self.company_name = result["company_name"];
                self.cac_autre = result["cac_autre"];
                self.entree_autre = result["entree_autre"];
                // les différentes dates de la périodes affichées dans la section 1
                if (la_data["start_date"] !== "") {
                    self.default_start_date = la_data["start_date"];
                    self.default_end_date = la_data["end_date"];
                }
            });
            return $.when(def1);
        },

        render_dashboards: function () {
            var self = this;
            _.each(this.dashboards_templates, function (template) {
                self
                    .$(".o_ro_dashboard")
                    .append(QWeb.render(template, { widget: self }));
            });
        },

        //Permet l'affiche des différents graph
        render_graphs: function () {
            var self = this;
            self.render_sale_report_graph();
            self.render_ateliers_report_graph();
            self.render_invoice_report_graph();
        },

        pos_order_today: function (e) {
            var self = this;
            var date = new Date();
            var yesterday = new Date(date.getTime());
            yesterday.setDate(date.getDate() - 1);
            e.stopPropagation();
            e.preventDefault();

            session.user_has_group("hr.group_hr_user").then(function (has_group) {
                if (has_group) {
                    var options = {
                        on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                    };
                    self.do_action(
                        {
                            name: _t(">Total entrées"),
                            type: "ir.actions.act_window",
                            res_model: "repair.order",
                            view_mode: "tree,form,calendar",
                            view_type: "form",
                            views: [
                                [false, "list"],
                                [false, "form"],
                            ],
                            domain: [],
                            target: "current",
                        },
                        options
                    );
                }
            });
        },
        pos_refund_orders: function (e) {
            var self = this;
            var date = new Date();
            var yesterday = new Date(date.getTime());
            yesterday.setDate(date.getDate() - 1);
            e.stopPropagation();
            e.preventDefault();
        },
        pos_refund_today_orders: function (e) {
            var self = this;
            var date = new Date();
            var yesterday = new Date(date.getTime());
            yesterday.setDate(date.getDate() - 1);
            e.stopPropagation();
            e.preventDefault();

            session.user_has_group("hr.group_hr_user").then(function (has_group) {
                if (has_group) {
                    var options = {
                        on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                    };
                    self.do_action(
                        {
                            name: _t("Total chiffre d'affaires comptabilité"),
                            type: "ir.actions.act_window",
                            res_model: "repair.order",
                            view_mode: "tree,form,calendar",
                            view_type: "form",
                            views: [
                                [false, "list"],
                                [false, "form"],
                            ],
                            domain: [],
                            target: "current",
                        },
                        options
                    );
                }
            });
        },
        pos_order: function (e) {
            var self = this;
            var date = new Date();
            var yesterday = new Date(date.getTime());
            yesterday.setDate(date.getDate() - 1);
            e.stopPropagation();
            e.preventDefault();
            session.user_has_group("hr.group_hr_user").then(function (has_group) {
                if (has_group) {
                    var options = {
                        on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                    };

                    self.do_action(
                        {
                            name: _t("Total chiffre d'affaires vente"),
                            type: "ir.actions.act_window",
                            res_model: "repair.order",
                            view_mode: "tree,form,calendar",
                            view_type: "form",
                            views: [
                                [false, "list"],
                                [false, "form"],
                            ],
                            target: "current",
                        },
                        options
                    );
                }
            });
        },

        //affichage du graph ateliers
        render_ateliers_report_graph: function () {
            var self = this;
            var la_data = self.get_cookie();

            var ctx = self.$(".enters_report");
            if (la_data["start_date"] !== "") {
                var temp = self._rpc({
                    model: "repair.order",
                    method: "get_atelier_report",
                    args: [la_data],
                });
            } else {
                var temp = self._rpc({
                    model: "repair.order",
                    method: "get_atelier_report",
                });
            }

            temp.then(function (arrays) {
                var data = {
                    labels: arrays[1],
                    datasets: [
                        {
                            label: "Entrées",
                            data: arrays[0],
                            backgroundColor: [
                                "rgba(255, 99, 132,1)",
                                "rgba(54, 162, 235,1)",
                                "rgba(75, 192, 192,1)",
                                "rgba(153, 102, 255,1)",
                                "rgba(10,20,30,1)",
                            ],
                            borderColor: [
                                "rgba(255, 99, 132, 0.2)",
                                "rgba(54, 162, 235, 0.2)",
                                "rgba(75, 192, 192, 0.2)",
                                "rgba(153, 102, 255, 0.2)",
                                "rgba(10,20,30,0.3)",
                            ],
                            borderWidth: 1,
                        },
                    ],
                };

                // options
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: " Entrées par ateliers",
                        fontSize: 18,
                        fontColor: "#111",
                    },
                    legend: {
                        display: false,
                        //              position: "bottom",
                        //              labels: {
                        //                fontColor: "#333",
                        //                fontSize: 16
                        //              }
                    },
                    scales: {
                        yAxes: [
                            {
                                ticks: {
                                    min: 0,
                                },
                            },
                        ],
                    },
                };

                //create Chart class object
                var chart = new Chart(ctx, {
                    type: "horizontalBar",
                    data: data,
                    options: options,
                });
            });
        },

        //affichage du graph chiffre d'affaires vente
        render_sale_report_graph: function () {
            var self = this;
            var ctx = self.$(".sale_report_graph");
            rpc
                .query({
                    model: "repair.order",
                    method: "get_sale_report",
                })
                .then(function (arrays) {
                    var data = {
                        labels: arrays[1],
                        datasets: [
                            {
                                label: "",
                                data: arrays[0],
                                backgroundColor: [
                                    "rgb(148, 22, 227)",
                                    "rgba(54, 162, 235)",
                                    "rgba(75, 192, 192)",
                                    "rgba(153, 102, 255)",
                                    "rgba(10,20,30)",
                                ],
                                borderColor: [
                                    "rgba(255, 99, 132,)",
                                    "rgba(54, 162, 235,)",
                                    "rgba(75, 192, 192,)",
                                    "rgba(153, 102, 255,)",
                                    "rgba(10,20,30,)",
                                ],
                                borderWidth: 1,
                            },
                        ],
                    };

                    //options
                    var options = {
                        responsive: true,
                        title: {
                            display: true,
                            position: "top",
                            text: "Chiffre d'affaires vente",
                            fontSize: 18,
                            fontColor: "#111",
                        },
                        legend: {
                            display: true,
                            position: "bottom",
                            labels: {
                                fontColor: "#333",
                                fontSize: 16,
                            },
                        },
                        scales: {
                            yAxes: [
                                {
                                    ticks: {
                                        min: 0,
                                    },
                                },
                            ],
                        },
                    };

                    //create Chart class object
                    var chart = new Chart(ctx, {
                        type: "pie",
                        data: data,
                        options: options,
                    });
                });
        },

        //affichage du graph chiffre d'affaires comptabilité
        render_invoice_report_graph: function () {
            var self = this;
            var ctx = self.$(".invoice_report_graph");
            rpc
                .query({
                    model: "repair.order",
                    method: "get_invoice_report",
                })
                .then(function (arrays) {
                    var data = {
                        labels: arrays[1],
                        datasets: [
                            {
                                label: "",
                                data: arrays[0],
                                backgroundColor: [
                                    "rgb(148, 22, 227)",
                                    "rgba(54, 162, 235)",
                                    "rgba(75, 192, 192)",
                                    "rgba(153, 102, 255)",
                                    "rgba(10,20,30)",
                                    "rgba(100,200,30)",
                                    "rgba(10,150,30)",
                                    "rgba(255,20,30)",
                                    "rgba(0,100,2)",
                                    "rgba(90,100,120)",
                                    "rgba(50,60,70)",
                                    "rgba(20,120,220)",
                                ],
                                borderColor: [
                                    "rgba(255, 99, 132,)",
                                    "rgba(54, 162, 235,)",
                                    "rgba(75, 192, 192,)",
                                    "rgba(153, 102, 255,)",
                                    "rgba(10,20,30,)",
                                    "rgba(100,200,30)",
                                    "rgba(10,150,30)",
                                    "rgba(255,20,30)",
                                    "rgba(0,100,2)",
                                    "rgba(90,100,120)",
                                    "rgba(50,60,70)",
                                    "rgba(20,120,220)",
                                ],
                                borderWidth: 1,
                            },
                        ],
                    };

                    //options
                    var options = {
                        responsive: true,
                        title: {
                            display: true,
                            position: "top",
                            text: "Chiffre d'affaires HT",
                            fontSize: 18,
                            fontColor: "#111",
                        },
                        legend: {
                            display: true,
                            position: "bottom",
                            labels: {
                                fontColor: "#333",
                                fontSize: 16,
                            },
                        },
                        scales: {
                            yAxes: [
                                {
                                    ticks: {
                                        min: 0,
                                    },
                                },
                            ],
                        },
                    };

                    //create Chart class object
                    var chart = new Chart(ctx, {
                        type: "pie",
                        data: data,
                        options: options,
                    });
                });
        },

        /* Fonction execute lors du clique sur le bouton de changement de date de filtre */
        change_dashboard: function () {
            location.reload();
            var self = this;
            self.set_used_date("0");
            self.recuperate_date();
            self.willStart();
            //        self.start();
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

            console.log(
                "obtention de la date appelée dans recuperate_date ========================",
                this.get_cookie()
            );
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

    core.action_registry.add("account_dashboard", RoDashboard);

    return RoDashboard;
});
