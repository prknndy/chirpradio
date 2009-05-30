###
### Copyright 2009 The Chicago Independent Radio Project
### All Rights Reserved.
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###     http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
###

"""Views for the DJ Database."""

from django import http
from django.template import loader, Context, RequestContext
from auth.decorators import require_role
from auth import roles
from djdb import models
from djdb import search


def landing_page(request):
    template = loader.get_template('djdb/landing_page.html')
    ctx_vars = { 'title': 'DJ Database' }
    if request.method == "POST":
        query_str = request.POST.get("query")
        if query_str:
            matching_keys = search.fetch_keys_for_query_string(query_str)
            segmented = search.load_and_segment_keys(matching_keys)
            ctx_vars["query_str"] = query_str
            ctx_vars["query_results"] = segmented
    ctx = RequestContext(request, ctx_vars)
    return http.HttpResponse(template.render(ctx))


def image(request):
    img = models.DjDbImage.get_by_url(request.path)
    if img is None:
        return http.HttpResponse(status=404)
    return http.HttpResponse(content=img.image_data,
                             mimetype=img.image_mimetype)

def artists_all(request):
    all_artist_names = []
    # Reads all of the artist names from the datastore in batches
    # of 1000 (which is the limit for datastore fetches).
    while True:
        query = models.Artist.all().order("name")
        saw_one = False
        for artist in query.fetch(limit=1000, offset=len(all_artist_names)):
            all_artist_names.append(artist.name)
            saw_one = True
        if not saw_one:
            break
    all_artist_names.append("")  # To force a trailing newline
    return http.HttpResponse(mimetype='text/plain; charset="utf-8"',
                             content=u"\n".join(all_artist_names))
 

# Only the music director has the power to add new artists.
@require_role(roles.MUSIC_DIRECTOR)
def artists_bulk_add(request):
    tmpl = loader.get_template("djdb/artists_bulk_add.html")
    ctx_vars = {}
    # Our default is the data entry screen, where users add a list
    # of artists in a textarea.
    mode = "data_entry"
    if request.method == "POST" and request.path.endswith(".confirm"):
        bulk_input = request.POST.get("bulk_input")
        artists_to_add = [line.strip() for line in bulk_input.split("\r\n")]
        artists_to_add = sorted(line for line in artists_to_add if line)
        # TODO(trow): Should we do some sort of checking that an artist
        # doesn't already exist?
        if artists_to_add:
            ctx_vars["artists_to_add"] = artists_to_add
            mode = "confirm"
        # If the textarea was empty, we fall through.  Since we did not
        # reset the mode, the user will just get another textarea to
        # enter names into.
    elif request.method == "POST" and request.path.endswith(".do"):
        artists_to_add = request.POST.getlist("artist_name")
        # Add each artist to the datastore, indexing as we go.
        # TODO(trow): We should do this all in a transaction.
        idx = search.Indexer()
        for name in artists_to_add:
            art = models.Artist(name=name)
            art.save()
            idx.add_artist(art)
        idx.save()
        ctx_vars["num_artists_added"] = len(artists_to_add)
            
    ctx_vars[mode] = True
    ctx = RequestContext(request, ctx_vars)
    return http.HttpResponse(tmpl.render(ctx))
