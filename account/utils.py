from django.core.exceptions import ObjectDoesNotExist

def get_default_field(_model, lookup_string):
    try:
        default_obj = _model.objects.get(name=lookup_string)
        print('lookup string: ', lookup_string)
        print('default object: ', default_obj)
        print('default key: ', default_obj.id)
        return default_obj
    except:
        pass
