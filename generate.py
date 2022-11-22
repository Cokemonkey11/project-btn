
import os, sys

import json, datetime, time

from subprocess import call

from git         import Repo, NoSuchPathError, InvalidGitRepositoryError
from PIL         import Image
from imgurpython import ImgurClient


if __name__ == "__main__":
    active  = Image.open('resource/bm_btn.png')
    passive = Image.open('resource/bm_pas.png')

    now = datetime.datetime.fromtimestamp(time.time())

    files = []
    uris  = []

    with open('config.json', 'r') as cfg:
        config = json.load(cfg)

    num_repos_size = len(str(len(config["repositories"])))
    active_age_max = int(config["days-for-active"])
    preview_paths  = config["preview-paths"]

    for index, repo in enumerate(config["repositories"]):
        simple_name = repo[0].split('/')[-1].split('.git')[0]

        assert len(simple_name) > 0

        tag = "[" + str(index + 1) + "/" + str(len(config["repositories"])).rjust(num_repos_size, ' ') + "]"
        print(tag + " Cloning shallow copy " + simple_name.ljust(20, ' ') + " - please wait a few minutes.")
        sys.stdout.flush()

        try:
            r = Repo('gen/' + simple_name)
        except (NoSuchPathError, InvalidGitRepositoryError) :
            print("No such path - clone anew...")
            r = Repo.clone_from(repo[0], 'gen/' + simple_name, depth=1)

        origin = r.remotes.origin

        cw = origin.config_writer
        cw.set('sparseCheckout', 'true')
        cw.release()

        fname = 'gen/' + simple_name + '/.git/info/sparse-checkout'
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        with open(fname, 'w') as sparse:
            for preview_path in preview_paths:
                sparse.write(simple_name + '/' + preview_path)

        origin.fetch(depth=1)
        r.git.reset('--hard', 'origin/master')

        date = datetime.datetime.fromtimestamp(int(r.rev_parse('HEAD').committed_date))
        age = (now - date).days
        if age > active_age_max:
            border = passive
        else:
            border = active

        qualified_preview_paths = ['gen/' + simple_name + '/' + f for f in preview_paths]
        valid_preview_paths     = [f for f in qualified_preview_paths if os.path.isfile(f)]
        preview_path            = next( (x for x in valid_preview_paths), None)
        if preview_path:
            f = Image.open(preview_path).resize((128, 128)).convert('RGBA')
            Image.alpha_composite(f, border).save('gen/' + simple_name + '.png', "PNG")
            files.append(('gen/' + simple_name + '.png', repo[1], age))
        else:
            print("  Don't have preview... skipping.")

    print("Accessing imgur API.")
    client = ImgurClient(config['imgur']['client-id'], config['imgur']['client-secret'])
    for path in sorted(files, key=lambda x: x[2]):
        print("  Uploading " + path[0] + " .")
        uris.append((client.upload_from_path(path[0])['link'], path[1]))

    with open('out.vbc', 'w') as f:
        print("Writing VB code file.")
        for uri in uris:
            f.write('[url=' + uri[1] + '][img]' + uri[0] + '[/img][/url]')

    print("Done.\n\n")
