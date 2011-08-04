package="fluxdgmenu"
version="1.0"

export prefix=/usr/local
export sysconfdir=/etc

CC=gcc
CFLAGS=-W -Wall -pedantic
LDFLAGS=-linotifytools
EXEC=usr/lib/fluxdgmenu/fxm-watch
SRC=usr/lib/fluxdgmenu/fxm-watch.c

fxm-watch:
	${CC} ${SRC} -o ${EXEC} ${LDFLAGS} ${CFLAGS}

.PHONY: clean install uninstall

clean:
	rm ${EXEC}
	rm -rf usr/share/locale/*

install:
	install -d ${prefix}/lib/fluxdgmenu
	install -m 0755 usr/lib/fluxdgmenu/* ${prefix}/lib/fluxdgmenu
	install -d ${prefix}/share/applications
	install -m 0755 usr/share/applications/* ${prefix}/share/applications
	./make-locale.sh
	install -d ${prefix}/share/locale
	cp -R usr/share/locale/* ${prefix}/share/locale
	install -d ${prefix}/share/desktop-directories
	install -m 0755 usr/share/desktop-directories/* ${prefix}/share/desktop-directories
	install -d ${prefix}/share/pixmaps
	install -m 0755 usr/share/pixmaps/* ${prefix}/share/pixmaps
	install -d ${sysconfdir}/xdg/menus
	install -m 0755 etc/xdg/menus/* ${sysconfdir}/xdg/menus
	install -d ${sysconfdir}/fluxdgmenu
	install -m 0755 etc/fluxdgmenu/* ${sysconfdir}/fluxdgmenu
	install -d ${prefix}/bin
	ln -sf -T ${prefix}/lib/fluxdgmenu/fxm-daemon ${prefix}/bin/fxm-daemon
	ln -sf -T ${prefix}/lib/fluxdgmenu/fxm-watch ${prefix}/bin/fxm-watch
	install -m 0755 debian/postinst /var/lib/dpkg/info/fluxdgmenu.postinst
	install -m 0755 debian/postrm /var/lib/dpkg/info/fluxdgmenu.postrm

uninstall:
	-rm -rf ${prefix}/lib/fluxdgmenu
	-rm -rf ${prefix}/share/locale/*/LC_MESSAGES/fluxdgmenu.mo
	-rm -f ${prefix}/share/desktop-directories/fxm-*.directory
	-rm -rf ${sysconfdir}/fluxdgmenu
	-rm -f ${sysconfdir}/xdg/menus/fxm-applications.menu
	-rm -f ${sysconfdir}/xdg/menus/fxm-rootmenu.menu
	-rm -f ${prefix}/bin/fxm-daemon
	-rm -f ${prefix}/bin/fxm-watch
	-rm -f /var/lib/dpkg/info/fluxdgmenu.postinst
	-rm -f /var/lib/dpkg/info/fluxdgmenu.postrm
