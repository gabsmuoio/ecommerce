from import_export import resources
from perfil.models import Perfil


class PerfilResource(resources.ModelResource):
    class Meta:
        model = Perfil
