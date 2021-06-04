# Steps

When all tests done and successful and PR is approved, follow these steps:

1. Bump version:
    1. Merge branch to master
    1. In your local git version of this repo
        1. Checkout master by: `git checkout master`
        1. Update local branch by: `git pull origin master`
        1. Bumpversion according to specifications, eg. `bumpversion <patch/minor/major>`
        1. Push commit directly to master `git push`
        1. Push commit directly to master `git push --tags`
1. Deploy on the appropriate server(s):
    1. Deploy on hasta:
        1. Deploy master to stage
            1. `ssh hasta`
            1. `us`
            1. Request stage environment `paxa` and follow instructions
            1. `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-demux-stage.sh master`
            1. Make sure that installation was successful
            1. `down`
        1. Deploy master to production
            1. `up`
            1. `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-demux-prod.sh`
