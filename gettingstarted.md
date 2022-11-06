---
layout: page
title: Getting Started
permalink: /gettingstarted/
nav_order: 2
---

# Getting Started with a GitHub Documentation Page!

## Installing Homebrew and Github on Mac OS

* Install Homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
* Install Git:
```
brew install git
```

## Cloning GitHub Repo to your local computer

This can be done either using the Git command line tool `git` or by using the GitHub desktop tool. The GitHub repo lives [here](https://github.com/bavc/bavc-resources). Use your [preferred method](https://www.youtube.com/watch?v=CKcqniGu3tA) to clone the repo to your local drive. You'll eventually need to navigate your terminal window to this repo using the `cd` command, so make sure you clone the repo somewhere that is easily accessible.


## Installing the rest of the software needed on Mac OS

*  Install [rbenv](https://github.com/rbenv/rbenv#installation)
```
brew install rbenv
```
* Set up rbenv for your shell:
```
rbenv init
```
* This might put out a message like this:

```
# Load rbenv automatically by appending
# the following to ~/.zshrc:

eval "$(rbenv init - zsh)"
```

* The above message is telling you that in order make sure that `rbenv` loads automatically you need to run the above command. This will setup your terminal to start rbenv on open. It actually puts that command in `bash_profile` which will automatically run every time you open a terminal window.
```
echo 'eval "$(rbenv init -)"' >> ~/.bash_profile
```
* More recent macOS versions have very tight security around system folders. to get around this we'll need to move the installation path of all the gems to your user folder (read ![this article](https://medium.com/@morgannegagne/what-is-a-ruby-gem-1eec2684e68) for more info on what gems are). Do that with the following commans:
```
echo 'GEM_HOME=$HOME/.gem' >> ~/.bash_profile
echo 'GEM_PATH=$HOME/.gem' >> ~/.bash_profile
```
* The above commans tell your terminal to start rbenv and change the Gem Paths to the user-definted paths at start. This is because the `bash_profile` is just a smalls script that runs whenever you open a terminal window. Once you've run these commans you can close and reopen your terminal window to make sure that all those setup commands are run. You can also run the following `source` command to run the `bash_profile` script to run all those commands
```
source ~/.bash_profile
```
* Check your installation (you should see a bunch of "OK"s)
```
curl -fsSL https://github.com/rbenv/rbenv-installer/raw/main/bin/rbenv-doctor | bash
```
* Install Ruby 2.7.2 using rbenv, which is not the latest version, but is the version required for GitHub Pages.
```
rbenv install 2.7.2
```

* Set Ruby 2.7.2 as your global version
Note: This will set version 2.7.2 as your default Ruby version. If you're working on other Ruby projects with the computer you're using for this workshop, feel free to contact us for help maintaining multiple versions.
```
rbenv global 2.7.2
```
* Restart your terminal

* Download / update Ruby gems:
```
gem update --system
```
* Install the jekyll and bundler gems.
```
gem install jekyll bundler
```


## Getting a local intance of the website running on your local server

* Navigate your terminal window to the Repository Directory using the `cd` command

* Run the following command
```
bundle install
```

* Now you can start the local server on your machine with the following command
```
bundle exec jekyll serve
```
You'll probably see something like this:
```
Configuration file: /Users/preservation/Documents/Github/bavc-resources/_config.yml
To use retry middleware with Faraday v2.0+, install `faraday-retry` gem
            Source: /Users/preservation/Documents/Github/bavc-resources
       Destination: /Users/preservation/Documents/Github/bavc-resources/_site
 Incremental build: disabled. Enable with --incremental
      Generating...
      Remote Theme: Using theme pmarsceill/just-the-docs
       Jekyll Feed: Generating feed for posts
                    done in 4.72 seconds.
 Auto-regeneration: enabled for '/Users/preservation/Documents/Github/bavc-resources'
    Server address: http://127.0.0.1:4000/bavc-resources/
  Server running... press ctrl-c to stop.
```

This means that you have a local instance of the page running at [http://127.0.0.1:4000/bavc-resources/](http://127.0.0.1:4000/bavc-resources/)

The purpose of running the local server on your machine is so that you can see the changes you're making to site. These changes will be made to the live site at [http://bavc.github.io/bavc-resources](http://bavc.github.io/bavc-resources) when you push them to the repo, but the local instance is as great way to test them beforehand.

## Making updates to the Resource Pages

### Github Etiquitte

Now that you have the repo clone and a local instance running on your computer you can make changes to the documentation and see them happen in real time before they're pushed to the main branch in the remote repository.

Proper GitHub etiquitte states that any changes you make should made to your own branch. When you're ready for these changes to be made to the main branch (what you see on the public website) you should create a ***Pull Request***, which pulls your changes into the main branch.

So, the first thing you need to do is create your own branch. [Here's an article](https://docs.couchbase.com/home/contribute/create-branches.html) about creating a new branch using Atom or the command line.

Once you've created a new branch you can push all the changes you want to this branch. Remember, the workflow for this is as follows:
* Make changes to the files
* *Stage* the changes
* *Commit* the changes with a helpful description/message
* *Push* the changes to your branch.

Once you're happy with all the changes you've pushed you can make a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request). Someone else on your team should review the Pull Request, then will confirm that it's all ok, and then it will *Merged* into the main branch of the remote repository.

### Making changes to the documentation

The documentation lives in text files that in the *Markdown* language. The [TemplateArticle.md]({{site.baseurl}}/docs/TemplateFolder/TemplateArticle.html) file contains all the different ways you can use Markdown to make pretty and readable documentation.

The files are best edited in a program like Atom or Visual Studio Code. These programs are a little confusing at first, so if you're lost you should watch a YouTube tutorial about them (as an added bonus, these programs integrate Git features like commits and pull requests into their GUIs).

Once you have a good editing environment setup all you have to do edit the text in the documents. Once you save the files you'll see the updates reflected instantly in your local instance.

### Adding a new Article

Articles all live in the `/docs/` folder, which is located in the root level of the repository. Inside `docs` there are a bunch of subfolders. Each of these subfolders represents a category of articles on the website. Inside each subfolder are a bunch of `.md` files. These files each correspond to an article. To make a new article you can simply copy an existing article, or copy the `TemplateArticle.md` file. Make sure you nest the new article in its associated subfolder, and that you update `layout`, `title`, and `parent` information at the top of the document.

### Adding a new subfolder / categeory

To add a new subfolder or category, you'll need to add a new subfolder to the `docs` folder. You'll also need to create a new `index.md` file inside of that folder. The `index.md` file is critical, as it tells the website that this new folder corresponds to a new category, and creates a landing page for that category. To make creating a new folder easier, you can just duplicate and rename the `TemplateFolder` directory. Just make sure you rename the folder, and rename `title` info in the header of the `index.md` file within that folder.
