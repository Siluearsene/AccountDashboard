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
            //'click .pos_order_today':'pos_order_today',
            //'click .pos_order':'pos_order',
            //'click .pos_total_sales':'pos_order',
            //'click .pos_session':'pos_session',
            //'click .pos_refund_orders':'pos_refund_orders',
            //'click .pos_refund_today_orders':'pos_refund_today_orders',
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
        return $.when(loadBundle(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
        var self = this;
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
      var def2 = self._rpc({
            model: "mini.account.dashboard",
            method: "get_information",
            args : [state],
        })
        .then(function (res) {
            self.payment_details = res['customer_data'];
            self.top_salesperson = res['cash_data'];
            self.selling_product = res['vendor_data'];
//            self.stock_value = res['stock_value'];
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

});


core.action_registry.add('account_dashboard', PosDashboard);

return PosDashboard;

});
