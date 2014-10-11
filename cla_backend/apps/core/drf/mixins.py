import jsonpatch

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import MethodNotAllowed


class NoParentReferenceException(BaseException):
    pass


class NestedGenericModelMixin(object):

    def get_parent_lookup_kwarg(self):
        return self.parent_prefix + '_' + self.lookup_field

    # def get_parent_queryset(self):
    #     return self.parent(requet=self.request).get_queryset()

    def get_parent_object(self):
        parent_key = self.kwargs.get(self.get_parent_lookup_kwarg(), None)
        if not parent_key:
            raise NoParentReferenceException('Trying to do a nested lookup on a non-nested viewset')
        parent_viewset_instance = self.parent(
            request=self.request,
            kwargs= {self.lookup_field: parent_key})
        parent_obj = parent_viewset_instance.get_object(
            queryset=parent_viewset_instance.get_queryset().select_related(None)
        )
        return parent_obj

    def get_parent_object_or_none(self):
        try:
            return self.get_parent_object()
        except (ObjectDoesNotExist, NoParentReferenceException):
            return None

    def is_one_to_one_nested(self):
        descriptor = getattr(self.parent.model, self.PARENT_FIELD)
        return not hasattr(descriptor, 'related')

    def get_object(self):
        if self.is_one_to_one_nested():
            return getattr(self.get_parent_object(), self.PARENT_FIELD)
        return super(NestedGenericModelMixin, self).get_object()

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'PARENT_FIELD'):
            raise Exception('To use this mixin you must specify PARENT_FIELD')
        super(NestedGenericModelMixin, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not self.is_one_to_one_nested():
            qs = getattr(self.get_parent_object(), self.PARENT_FIELD)
            return qs.all()

        return super(NestedGenericModelMixin, self).get_queryset()

    def post_save(self, obj, created=False):
        """
        associates `obj` to the parent
        :param kwargs: any kwargs needed to work out the parent
        :return: parent_obj after saving it
        """
        if not self.is_one_to_one_nested():
            return super(NestedGenericModelMixin, self).post_save(obj, created=created)

        if created:
            parent_obj = self.get_parent_object_or_none()

            if parent_obj:
                if getattr(parent_obj, self.PARENT_FIELD):
                    raise MethodNotAllowed('POST: %s already has a %s associated to it' % (parent_obj, obj.__class__.__name__))
                else:
                    setattr(parent_obj, self.PARENT_FIELD, obj)
                    parent_obj.save(update_fields=[self.PARENT_FIELD])

        super(NestedGenericModelMixin, self).post_save(obj, created=created)


class JsonPatchViewSetMixin(object):
    @property
    def jsonpatch(self):
        forwards = jsonpatch.JsonPatch.from_diff(self.__pre_save__, self.__post_save__)
        backwards = jsonpatch.JsonPatch.from_diff(self.__post_save__, self.__pre_save__)
        serializer = self.get_serializer_class()

        return {
            'serializer': '.'.join([serializer.__module__, serializer.__name__]),
            'backwards': backwards.patch,
            'forwards': forwards.patch
        }

    def pre_save(self, obj):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data

    def post_save(self, obj, created=False, **kwargs):
        super(JsonPatchViewSetMixin, self).post_save(obj, created=created)
        self.__post_save__ = self.get_serializer_class()(obj).data

        return obj
