from django.template.defaultfilters import slugify


def create_slug(c, key):
    slug = slugify(key)
    qs = c.objects.filter(slug=slug)
    exists = qs.exists()

    if exists:
        slug = "%s-%s" %(slug, qs.first().id)

    return slug