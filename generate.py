
import os

import json

def checkout_script(simple_name, repo, preview_path):
	return ("""
mkdir %s
cd    %s
git   init
git   remote add                 origin %s
git   config core.sparseCheckout true
echo  %s/%s > .git/info/sparse-checkout
git   pull   origin master --depth 1
cd    ..
""" % (simple_name, simple_name, repo, simple_name, preview_path))

with open('config.json', 'r') as cfg:
	config = json.load(cfg)

	for repo in config["repositories"]:
		simple_name = repo.split('/')[1].split('.git')[0]

		os.systm("bash -c '%s'" % checkout_script(simple_name, repo, config['previw_path']))
