#! /usr/bin/bash
INSTALL_LOC=/mnt/c/Program\ Files\ \(x86\)/Steam/steamapps/common/Valheim/
MODDIR=${INSTALL_LOC}BepInEx/plugins
COPYDIR=~/val/plugins
BEPINEX=(
    "BepInEx"
    "doorstop_libs"
    "doorstop_config.ini"
    "winhttp.dll"
)
BEPINCOPY=~/val/bepin

function copyBepInEx() {
    test -e ~/val/bepin || (echo "creating copy of BepInEx" && mkdir -p ~/val/bepin)
    for f in ${BEPINEX[@]}; do
        cp -r "${INSTALL_LOC}"/${f} ${BEPINCOPY}
    done
}

function printMods() {
    for f in "${COPYDIR}"/*.dll; do
        echo "> $(basename -- ${f%.*})"
    done
    for f in "${COPYDIR}"/**/*.dll; do
        echo "> $(basename -- ${f%.*})"
    done

}

function copyPluginMods() {
    test -e "${MODDIR}" && cd "${MODDIR}" || (echo "Failure" && exit)
    test -e ${COPYDIR} || (echo "Creating copy of mods in ${COPYDIR}" && mkdir -p ${COPYDIR})
    cp -r "${MODDIR}"/* ${COPYDIR}
    echo "Moved Mods:"
    printMods
}

function copyMods() {
    copyPluginMods
    copyBepInEx
}

function removeMods() {
    copyMods
    for f in ${BEPINEX[@]}; do
        rm -r "${INSTALL_LOC}"/${f}
    done
}

function install() {
    for f in ~/val/bepin/*; do
        cp -r ${f} "${INSTALL_LOC}"
    done
}

function fetch() {
    echo "Not Implemented"
}

cmd=$1

if [[ "${cmd}" == 'remove' ]]; then
    removeMods
elif [[ "${cmd}" == 'install' ]]; then
    install
elif [[ "${cmd}" == 'fetch' ]]; then
    fetch
elif [[ "${cmd}" == 'copy' ]]; then
    copyMods
fi
