
import os

import json

from subprocess import call

from git import Repo


if __name__ == "__main__":
    with open('config.json', 'r') as cfg:
        config = json.load(cfg)

        for repo in config["repositories"]:
            simple_name = repo.split('/')[1].split('.git')[0]

            r = Repo.init('gen/' + simple_name, bare=True)
            origin = r.create_remote('origin', repo)

            cw = r.config_writer()
            #cw.set('core.bare', 'false')
            cw.set('core.worktree', 'gen/' + simple_name)
            cw.release()

            cw = origin.config_writer
            #cw.set('core.bare', 'false')
            #cw.set('core.worktree', 'gen/' + simple_name)
            cw.set('sparseCheckout', 'true')
            cw.release()

            fname = 'gen/' + simple_name + '/.git/info/sparse-checkout'
            if not os.path.exists(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))
            with open(fname, 'w') as sparse:
                sparse.write(simple_name + '/' + config['preview-path'])

            origin.pull(depth=1)
