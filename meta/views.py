from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from . import settings


class Meta(object):
    """
    Helper for building context meta object
    """
    _keywords = []
    _url = None
    _image = None
    _defaults = {
        'use_sites': 'USE_SITES',
        'title': None,
        'description': None,
        'extra_props': None,
        'extra_custom_props': None,
        'custom_namespace': 'OG_NAMESPACES',
        'keywords': None,
        'url': None,
        'image': None,
        'object_type': 'SITE_TYPE',
        'site_name': 'SITE_NAME',
        'twitter_site': None,
        'twitter_creator': None,
        'twitter_card': None,
        'facebook_app_id': None,
        'locale': None,
        'use_og': 'USE_OG_PROPERTIES',
        'use_twitter': 'USE_TWITTER_PROPERTIES',
        'use_facebook': 'USE_FACEBOOK_PROPERTIES',
        'use_googleplus': 'USE_GOOGLEPLUS_PROPERTIES',
        'use_title_tag': 'USE_TITLE_TAG',
        'gplus_type': 'GPLUS_TYPE',
        'gplus_publisher': 'GPLUS_PUBLISHER',
        'gplus_author': 'GPLUS_AUTHOR',
        'fb_pages': 'FB_PAGES',
        'og_app_id': 'FB_APPID',
    }

    def __init__(self, **kwargs):
        for key, setting_name in self._defaults.items():
            default_value = getattr(settings, setting_name) if setting_name else None
            value = kwargs.get(key, default_value)
            setattr(self, key, value)

    def get_domain(self):
        if self.use_sites:
            from django.contrib.sites.models import Site
            return Site.objects.get_current().domain
        if not settings.SITE_DOMAIN:
            raise ImproperlyConfigured('META_SITE_DOMAIN is not set')
        return settings.SITE_DOMAIN

    def get_protocol(self):
        if not settings.SITE_PROTOCOL:
            raise ImproperlyConfigured('META_SITE_PROTOCOL is not set')
        return settings.SITE_PROTOCOL

    def get_full_url(self, url):
        if not url:
            return None
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            return '%s:%s' % (
                self.get_protocol(),
                url
            )
        if url.startswith('/'):
            return '%s://%s%s' % (
                self.get_protocol(),
                self.get_domain(),
                url
            )
        return '%s://%s/%s' % (
            self.get_protocol(),
            self.get_domain(),
            url
        )

    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        if keywords is None:
            kws = settings.DEFAULT_KEYWORDS
        else:
            if not hasattr(keywords, '__iter__'):
                # Not iterable
                raise ValueError('Keywords must be an intrable')
            kws = [k for k in keywords]
            if settings.INCLUDE_KEYWORDS:
                kws += settings.INCLUDE_KEYWORDS
        seen = set()
        seen_add = seen.add
        self._keywords = [k for k in kws if k not in seen and not seen_add(k)]

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = self.get_full_url(url)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        if image is None and settings.DEFAULT_IMAGE:
            image = settings.DEFAULT_IMAGE
        if image:
            if not image.startswith('http') and not image.startswith('/'):
                image = '%s%s' % (settings.IMAGE_URL, image)
            self._image = self.get_full_url(image)

    def merge(self, meta):
        kwargs = {key: getattr(self, key) for key in self._defaults.keys()}
        for key in self._defaults.keys():
            new_value = getattr(meta, key)
            if new_value:
                kwargs[key] = new_value
        return self.__class__(**kwargs)


class MetadataMixin(object):
    """
    Django CBV mixin to prepare metadata for the view context
    """
    meta_class = Meta
    context_meta_name = 'meta'

    title = None
    description = None
    extra_props = None
    extra_custom_props = None
    custom_namespace = None
    keywords = []
    url = None
    image = None
    object_type = None
    site_name = None
    twitter_site = None
    twitter_creator = None
    twitter_card = None
    facebook_app_id = None
    locale = None
    use_sites = False
    use_og = False
    use_use_title_tag = False
    gplus_type = None
    gplus_author = None
    gplus_publisher = None

    def __init__(self, **kwargs):
        self.use_sites = settings.USE_SITES
        self.use_og = settings.USE_OG_PROPERTIES
        self.use_title_tag = settings.USE_TITLE_TAG
        super(MetadataMixin, self).__init__(**kwargs)

    def get_meta_class(self):
        return self.meta_class

    def get_protocol(self):
        return settings.SITE_PROTOCOL

    def get_domain(self):
        return settings.SITE_DOMAIN

    def get_meta_title(self, context=None):
        return self.title

    def get_meta_description(self, context=None):
        return self.description

    def get_meta_keywords(self, context=None):
        return self.keywords

    def get_meta_url(self, context=None):
        return self.url

    def get_meta_image(self, context=None):
        return self.image

    def get_meta_object_type(self, context=None):
        return self.object_type or settings.SITE_TYPE

    def get_meta_site_name(self, context=None):
        return self.site_name or settings.SITE_NAME

    def get_meta_extra_props(self, context=None):
        return self.extra_props

    def get_meta_extra_custom_props(self, context=None):
        return self.extra_custom_props

    def get_meta_custom_namespace(self, context=None):
        return self.custom_namespace or settings.OG_NAMESPACES

    def get_meta_twitter_site(self, context=None):
        return self.twitter_site

    def get_meta_twitter_creator(self, context=None):
        return self.twitter_creator

    def get_meta_twitter_card(self, context=None):
        return self.twitter_card

    def get_meta_facebook_app_id(self, context=None):
        return self.facebook_app_id

    def get_meta_gplus_type(self, context=None):
        return self.gplus_type

    def get_meta_gplus_author(self, context=None):
        return self.gplus_author

    def get_meta_gplus_publisher(self, context=None):
        return self.gplus_publisher

    def get_meta_locale(self, context=None):
        return self.locale

    def get_meta(self, context=None):
        return self.get_meta_class()(
            use_og=self.use_og,
            use_title_tag=self.use_title_tag,
            use_sites=self.use_sites,
            title=self.get_meta_title(context=context),
            description=self.get_meta_description(context=context),
            extra_props=self.get_meta_extra_props(context=context),
            extra_custom_props=self.get_meta_extra_custom_props(context=context),
            custom_namespace=self.get_meta_custom_namespace(context=context),
            keywords=self.get_meta_keywords(context=context),
            image=self.get_meta_image(context=context),
            url=self.get_meta_url(context=context),
            object_type=self.get_meta_object_type(context=context),
            site_name=self.get_meta_site_name(context=context),
            twitter_site=self.get_meta_twitter_site(context=context),
            twitter_creator=self.get_meta_twitter_creator(context=context),
            twitter_card=self.get_meta_twitter_card(context=context),
            locale=self.get_meta_locale(context=context),
            facebook_app_id=self.get_meta_facebook_app_id(context=context),
            gplus_type=self.get_meta_gplus_type(context=context),
            gplus_author=self.get_meta_gplus_author(context=context),
            gplus_publisher=self.get_meta_gplus_publisher(context=context),
        )

    def get_context_data(self, **kwargs):
        context = super(MetadataMixin, self).get_context_data(**kwargs)
        context[self.context_meta_name] = self.get_meta(context=context)
        return context
