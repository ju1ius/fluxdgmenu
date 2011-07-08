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

install:
	install -d ${prefix}/lib/fluxdgmenu
	install -m 0755 usr/lib/fluxdgmenu/* ${prefix}/lib/fluxdgmenu
	install -d ${prefix}/share/desktop-directories
	install -m 0755 usr/share/desktop-directories/* ${prefix}/share/desktop-directories
	install -d ${sysconfdir}/xdg/menus
	install -m 0755 etc/xdg/menus/fxm-applications.menu ${sysconfdir}/xdg/menus
	install -d ${sysconfdir}/fluxdgmenu
	install -m 0755 etc/fluxdgmenu/* ${sysconfdir}/fluxdgmenu
	install -d ${prefix}/bin
	ln -sf -T ${prefix}/lib/fluxdgmenu/fxm-daemon ${prefix}/bin/fxm-daemon
	ln -sf -T ${prefix}/lib/fluxdgmenu/fxm-watch ${prefix}/bin/fxm-watch

uninstall:
	-rm -rf ${prefix}/lib/fluxdgmenu
	-rm -rf ${prefix}/share/desktop-directories/fxm-*.directory
	-rm -rf ${sysconfdir}/fluxdgmenu
	-rm -f ${sysconfdir}/xdg/menus/fxm-applications.menu
	-rm -f ${prefix}/bin/fxm-daemon
	-rm -f ${prefix}/bin/fxm-watch
