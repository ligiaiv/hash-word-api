#/bin/bash

# Temas
time python3 cache_requests.py --top_words 60 -c=tema-negros
time python3 cache_requests.py --top_words 60 -c=tema-lgbt
time python3 cache_requests.py --top_words 60 -c=tema-genero
time python3 cache_requests.py --top_words 60 -c=tema-indigena

time python3 cache_requests.py --top_words 1440 -c=tema-negros
time python3 cache_requests.py --top_words 1440 -c=tema-lgbt
time python3 cache_requests.py --top_words 1440 -c=tema-genero
time python3 cache_requests.py --top_words 1440 -c=tema-indigena

exit 0;

