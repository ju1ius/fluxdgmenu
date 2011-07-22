#! /bin/bash

localedir="$1"
if [[ ! -d "$1" ]]
then
  echo "$1 is not a directory !"
fi

po_dir="./po"
domain="fluxdgmenu"

rm -rf "./usr/lib/fluxdgmenu/locale"

find "$po_dir" -name *.po | while read po_file
do
  language=$(basename $po_file '.po')
  domain_dir="$localedir/$language/LC_MESSAGES"
  mkdir -p "$domain_dir"
  msgfmt -o "$domain_dir/$domain.mo" "$po_file"
done
