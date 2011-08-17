#! /bin/bash

app_dir=$(dirname $(readlink -f $0))
po_dir=$app_dir/../po
locale_dir=$app_dir/../usr/share/locale
domain="fluxdgmenu"

rm -rf $locale_dir/* 2> /dev/null

echo "=============================="
echo "Building localized messages..."

#find "$po_dir" -name *.po | while read po_file
for po_file in $po_dir/*.po
do
  language=$(basename $po_file '.po')
  language_dir="$locale_dir/$language/LC_MESSAGES"
  mkdir -p "$language_dir"
  msgfmt -o "$language_dir/$domain.mo" "$po_file"
done

exit 0
