#! /bin/bash

localedir="$1"
if [[ ! -d "$1" ]]
then
  echo "$1 is not a directory !"
  exit 1
fi

app_dir=$(dirname $0)
po_dir=$app_dir/po
domain="fluxdgmenu"

rm -rf "$app_dir/usr/share/locale"

find "$po_dir" -name *.po | while read po_file
do
  language=$(basename $po_file '.po')
  language_dir="$locale_dir/$language/LC_MESSAGES"
  mkdir -p "$language_dir"
  msgfmt -o "$language_dir/$domain.mo" "$po_file"
done
