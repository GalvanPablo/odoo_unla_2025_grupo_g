{
    "name": "Inmobiliaria",
    "version": "1.0",
    "author": "UNLa-Grupo-G",
    "category": "UNLa",
    "description": "Modulo creado para la catedra de Programación de Sistemas ERP con Odoo",
    "depends": [
        "base"
    ],
    "data": [
        "security/real_estate_res_groups.xml",
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_offer_views.xml",  
        "views/estate_property_tag_views.xml",
        "views/real_estate_menuitem.xml",
        'views/res_users_views.xml'
    ],
    "application": True,
    "installable": True
}
