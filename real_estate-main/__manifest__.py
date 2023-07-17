
{
    'name': "Real-Estate Management",

    'summary': """
        A real estate module where one can add properties info 
        for advertising purposes""",

    'description': """

        This is a test module of Real-Estate Management!

        Written for the Odoo Quickstart Tutorial.

        """,

    'author': "Osama Imran",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'estate_module'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,

    'auto_install': False,

    'application': False,
}
