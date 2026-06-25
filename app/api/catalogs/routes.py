from . import catalogs
from .views import CatalogPersonnel, CatalogOrganizations, CatalogEquipment

catalogs.add_url_rule('/personnel', view_func=CatalogPersonnel.as_view('personnel'))
catalogs.add_url_rule('/organization', view_func=CatalogOrganizations.as_view('catalog_organization'))
catalogs.add_url_rule('/equipment', view_func=CatalogEquipment.as_view('catalog_equipment'))