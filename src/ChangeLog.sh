#! /bin/bash

git log --pretty=format:'%h %ad %an%n    %s%n' --date=short release-3.0.0..HEAD > ChangeLog.txt
