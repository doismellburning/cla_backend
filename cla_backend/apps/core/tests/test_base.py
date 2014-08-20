from django.core.urlresolvers import reverse

from rest_framework import status

from core.tests.mommy_utils import make_recipe


class CLABaseApiTestMixin(object):
    """
    Useful testing methods


    NOTE: you probably don't want to subclass it directly.
        Think if it's better to use SimpleResourceAPIMixin or NestedSimpleResourceAPIMixin
        instead.
    """
    API_URL_NAMESPACE = None

    def get_http_authorization(self, token=None):
        if not token:
            return ''
        return 'Bearer %s' % token

    # NOT ALLOWED SHORTCUTS

    def _test_get_not_allowed(self, url, token=None):
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_post_not_allowed(self, url, data={}, token=None):
        response = self.client.post(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_put_not_allowed(self, url, data={}, token=None):
        response = self.client.put(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_patch_not_allowed(self, url, data={}, token=None):
        response = self.client.patch(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def _test_delete_not_allowed(self, url, token=None):
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # NOT AUTHORIZED SHORTCUTS

    def _test_get_not_authorized(self, url, token=None):
        response = self.client.get(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_post_not_authorized(self, url, data={}, token=None):
        response = self.client.post(
            url, data, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_put_not_authorized(self, url, data={}, token=None):
        response = self.client.put(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_patch_not_authorized(self, url, data={}, token=None):
        response = self.client.patch(
            url, data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_delete_not_authorized(self, url, token=None):
        response = self.client.delete(
            url, HTTP_AUTHORIZATION=self.get_http_authorization(token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SimpleResourceAPIMixin(CLABaseApiTestMixin):
    """
    You should (almost) always subclass this or the NestedSimpleResourceAPIMixin
    in your TestCase.

    Your actual TestCase should also sublass one of the legalaid.tests.views.test_base
    classes.


    Usage:

    when using it, override the config properties below (in UPPERCASE).

    your test will have:
        * self.resource ==> instance of the resource you are about to test
        * self.list_url, self.details_url ==> url to list and details
        * a bunch of extra things (look around)
    """
    LOOKUP_KEY = 'pk'
    API_URL_BASE_NAME = None
    RESOURCE_RECIPE = None

    @property
    def response_keys(self):
        return []

    @property
    def resource_lookup_value(self):
        return getattr(self.resource, self.LOOKUP_KEY)

    def assertResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            self.response_keys
        )

    def get_list_url(self):
        return reverse(
            '%s:%s-list' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME)
        )

    def get_detail_url(self, resource_lookup_value, suffix='detail'):
        return reverse(
            '%s:%s-%s' % (self.API_URL_NAMESPACE, self.API_URL_BASE_NAME, suffix),
            args=(), kwargs={self.LOOKUP_KEY: unicode(resource_lookup_value)}
        )

    def _create(self, data=None, url=None):
        if not data: data = {}
        if not url: url = self.get_list_url()
        return self.client.post(
            url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

    def setUp(self):
        super(SimpleResourceAPIMixin, self).setUp()
        self.resource = self.make_resource()

    @property
    def list_url(self):
        return self.get_list_url()

    @property
    def detail_url(self):
        return self.get_detail_url(self.resource_lookup_value)

    def make_resource(self, **kwargs):
        return make_recipe(self.RESOURCE_RECIPE, **kwargs)


class NestedSimpleResourceAPIMixin(SimpleResourceAPIMixin):
    """
    You should (almost) always subclass this or the SimpleResourceAPIMixin
    in your TestCase.

    Your actual TestCase should also sublass one of the legalaid.tests.views.test_base
    classes.

    Usage:

    when using it, override the config properties below (in UPPERCASE).

    your test will have:
        * self.resource ==> instance of the resource you are about to test
        * self.parent_resource ==> instance of the parent resource
        * self.list_url, self.details_url ==> url to list and details
        * a bunch of extra things (look around)
    """

    LOOKUP_KEY = None  # e.g. case_reference
    PARENT_LOOKUP_KEY = None  # e.g. reference
    PARENT_RESOURCE_RECIPE = None  # e.g. legalaid.case
    PARENT_PK_FIELD = None  # e.g. eligibility_check

    @property
    def resource_lookup_value(self):
        return getattr(self.parent_resource, self.PARENT_LOOKUP_KEY)

    def get_list_url(self):
        return None

    def setUp(self):
        super(NestedSimpleResourceAPIMixin, self).setUp()
        self.parent_resource = self.make_parent_resource()

    def make_parent_resource(self, **kwargs):
        kwargs[self.PARENT_PK_FIELD] = self.resource

        return make_recipe(
            self.PARENT_RESOURCE_RECIPE, **kwargs
        )

    def _cleanup_before_create(self):
        setattr(self.parent_resource, self.PARENT_PK_FIELD, None)
        self.parent_resource.save()

    def _create(self, data=None, url=None):
        self._cleanup_before_create()
        return self.client.post(
            url or self.detail_url, data=data or {}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
