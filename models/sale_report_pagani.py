# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    vehicle_id = fields.Many2one('fleet.vehicle', 'Véhicule', readonly=True)
    ro_id = fields.Many2one('repair.order', "Ordre de réparation")
    category_type = fields.Selection([
        ('mechanical', "Catégorie Mécanique"),
        ('sheet_metal', "Catégorie Tôlerie"),
        ('painting', "Catégorie Peinture")
    ], readonly=True)

    @property
    def _table_query(self):
        with_ = self._with_sale()
        select = self._select_sale() + ", vehicle.id AS vehicle_id, ro.id AS ro_id, l.category_type AS category_type"
        from_q = self._from_sale() + """
                                        LEFT JOIN repair_order ro ON s.repair_order_id = ro.id
                                        LEFT JOIN fleet_vehicle vehicle ON ro.vehicle_id = vehicle.id
                                    """
        groupby = self._group_by_sale() + ", l.category_type, vehicle.id, ro.id"

        query = f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {select}
            FROM {from_q}
            WHERE {self._where_sale()}
            GROUP BY {groupby}
            {")" if with_ else ""}
        """
        return query
