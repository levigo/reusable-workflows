#!/usr/bin/env bash

tag_name=latest

git tag -d $tag_name ;
git push --delete origin $tag_name ;
git tag $tag_name ;
git push origin $tag_name ;
