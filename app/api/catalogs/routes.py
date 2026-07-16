from . import catalogs
from .views import CatalogPersonnel, CatalogOrganization, CatalogEquipment, CatalogRoles

catalogs.add_url_rule('/personnel', view_func=CatalogPersonnel.as_view('personnel'))
catalogs.add_url_rule('/organization', view_func=CatalogOrganization.as_view('catalog_organization'))
catalogs.add_url_rule('/equipment', view_func=CatalogEquipment.as_view('catalog_equipment'))
catalogs.add_url_rule('/roles', view_func=CatalogRoles.as_view('catalog_roles'))