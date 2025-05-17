from django.urls import resolve, reverse
from django.conf import settings
from django.utils.translation import get_language

class HreflangMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if response.status_code == 200:
                current_language = get_language()

                alternate_links = []
                for lang_code, lang_name in settings.LANGUAGES:
                    if lang_code != current_language:
                        view = resolve(request.path_info)
                        namespace = view.namespace
                        url_name = view.url_name
                        url_kwargs = view.kwargs
                        url = reverse(f'{namespace}:{url_name}', kwargs=url_kwargs, args=None)
                        alternate_links.append(
                            f'<link rel="alternate" hreflang="{lang_code}" href="{request.scheme}://{request.get_host()}{url.replace(current_language, lang_code)}">'
                        )
                alternate_links = '\n'.join(alternate_links)

                current_url = request.get_full_path()
                canonical_link = f'<link rel="canonical" href="{request.scheme}://{request.get_host()}{current_url}">'

                response.content = response.content.replace(
                    b'<head>', 
                    f'<head>\n{alternate_links}\n{canonical_link}'.encode()
                )
        except:
            pass 

        return response
