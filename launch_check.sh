#!/bin/bash

cat << 'EOF' > ./pars.sh
#!/bin/bash
echo -e "########\e[31m Проверка пакетов для работы скрипта\e[0m########"
source check_pack.sh
source ini.sh
echo -e "########\e[31m 1 Настройки файла initrc_\e[0m########"
export "pars"
export "pars2"
LOG0=/tmp/log0
FILE_NAME="$pars"
export set_pwd="$PWD"
if [ -e "$FILE_NAME" ];then
###
function search(){
text=$1
log=$2
echo -n > $log
while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $log
  fi
done < $FILE_NAME
sed -i 's/"//g' $log
}

log_s=/tmp/log3
log_t=/tmp/log2
log_tm=/tmp/log4
log_dns_zl=/tmp/log5
log_dns=/tmp/log6
log_dns1=/tmp/log6_1
log_net=/tmp/log7
log_ntp=/tmp/log8
export log_dns_zg=/tmp/log9
log_mtu=/tmp/log10

text_s="REPO_IP/"
text_t="REPO_IP="
text_tm="TIMEZONE_FILE="
text_dns_zl="DNS_ZONE="
text_net="NET="
text_dns="CLOUD_DNS"
text_dns1="NET"
text_ntp="EXTERNAL_NTP"
text_dns_zg="CLOUD_ZONE="
text_mtu="MTU="

args=(
  "$text_tm" "$log_tm"
  "$text_s" "$log_s"
  "$text_t" "$log_t"
  "$text_dns_zl" "$log_dns_zl"
  "$text_net" "$log_net"
  "$text_dns" "$log_dns"
  "$text_ntp" "$log_ntp"
  "$text_dns_zg" "$log_dns_zg"
  "$text_mtu" "$log_mtu"
)

for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done


###
echo -n "" > "$LOG0"

echo -n > $log_dns1
function glue() {
text=$1
log=$2

while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $log
  fi
done < $log_dns
}

args1=(
  "$text_dns1" "$log_dns1"

)

for (( i=0; i<${#args1[@]}; i+=2 )); do
  glue "${args1[i]}" "${args1[i+1]}"
done
####
while read line; do
    echo "MTU $line"
done < $log_mtu > $LOG0

###glue+ip+dns
log=$(cat $log_net)
while read line; do
  echo "DNS ${log}${line}" >> $LOG0
done < $log_dns1

####
cat "$log_tm" "$log_dns_zl" "$log_dns_zg" >> $LOG0
###+http+glue
log=$(cat $log_t)

while read line; do
  echo "http://${log}/${line}" >> $LOG0
done < $log_s

### IP NTP
regex="([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
while read -r line; do
    if [[ "$line" =~ $regex ]]; then
        ip="${BASH_REMATCH[1]}"
        echo "NTP $ip" >> "$LOG0"
    fi
done < "$log_ntp"
cat "$LOG0" > endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars2.sh"

else

echo -e "\e[31m 1 No file $FILE_NAME \e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" > endpars
   source "$set_pwd/pars2.sh"
fi

EOF
chmod 775 ./pars.sh

cat << 'EOF' > ./pars2.sh
#!/bin/bash
echo -e "########\e[31m 2 Настройки файла initrc_2\e[0m########"
LOG0=/tmp/log00
FILE_NAME="$pars2"
if [ -e "$FILE_NAME" ];then
###
function search(){
text=$1
log=$2
echo -n > $log
while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $log
  fi
done < $FILE_NAME
sed -i 's/"//g' $log
}

log_s=/tmp/log3
log_t=/tmp/log2
log_tm=/tmp/log4
log_dns_zl=/tmp/log5
log_dns=/tmp/log6
log_dns1=/tmp/log6_1
log_net=/tmp/log7
log_ntp=/tmp/log8
log_dns_zg=/tmp/log9
log_mtu=/tmp/log10

text_s="REPO_IP/"
text_t="REPO_IP="
text_tm="TIMEZONE_FILE="
text_dns_zl="DNS_ZONE="
text_net="NET="
text_dns="CLOUD_DNS"
text_dns1="NET"
text_ntp="EXTERNAL_NTP"
text_dns_zg="CLOUD_ZONE="
text_mtu="MTU="

args=(
  "$text_tm" "$log_tm"
  "$text_s" "$log_s"
  "$text_t" "$log_t"
  "$text_dns_zl" "$log_dns_zl"
  "$text_net" "$log_net"
  "$text_dns" "$log_dns"
  "$text_ntp" "$log_ntp"
  "$text_dns_zg" "$log_dns_zg"
  "$text_mtu" "$log_mtu"

)

for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done

#cat log3
#cat log4
#cat log2
###
echo -n "" > "$LOG0"

echo -n > $log_dns1
function glue() {
text=$1
log=$2

while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $log
  fi
done < $log_dns
}

args1=(
  "$text_dns1" "$log_dns1"

)

for (( i=0; i<${#args1[@]}; i+=2 )); do
  glue "${args1[i]}" "${args1[i+1]}"
done
####
while read line; do
    echo "MTU $line"
done < $log_mtu > $LOG0

###glue+ip+dns
log=$(cat $log_net)
while read line; do
  echo "DNS ${log}${line}" >> $LOG0
done < $log_dns1

####
cat "$log_tm" "$log_dns_zl" "$log_dns_zg" >> $LOG0
###+http+glue
log=$(cat $log_t)

while read line; do
  echo "http://${log}/${line}" >> $LOG0
done < $log_s

### IP NTP
regex="([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
while read -r line; do
    if [[ "$line" =~ $regex ]]; then
        ip="${BASH_REMATCH[1]}"
        echo "NTP $ip" >> "$LOG0"
    fi
done < "$log_ntp"
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars3.sh"
else
echo -e "\e[31m 2 No File "$FILE_NAME" \e[0m"
echo -e  "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
source "$set_pwd/pars3.sh"

fi

EOF

chmod 775 ./pars2.sh

cat << 'EOF' > ./pars3.sh
#!/bin/bash
echo -e "########\e[31m 3 Настройки файла resolv.conf\e[0m########"
FILE_NAME3="/etc/resolv.conf"
LOG0="/tmp/log000"
if [ -e "$FILE_NAME" ];then
FILE_NAME3="/etc/resolv.conf"
LOG0="/tmp/log000"
log="$(mktemp)"
while read line; do
  if [[ "$line" == *"nameserver"* ]]; then
    echo "${line#*nameserver}" >> "$log"
  fi
done < $FILE_NAME3
####
while read line; do
    echo "Name server $line"
done < $log > $LOG0
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars4.sh"
else
echo -e "\e[31m######## 3 No file $FILE_NAME3 ########\e[0m"
echo -e "No File $FILE_NAME3" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars4.sh"

fi
EOF

chmod 775 ./pars3.sh
cat << 'EOF' > ./pars4.sh
#!/bin/bash
echo -e "########\e[31m 4 Настройки файла settings.yaml\e[0m########"
FILE_NAME="/etc/cobbler/settings.yaml"
LOG0=/tmp/log0000
if [ -e "$FILE_NAME" ];then
###
function search(){
text=$1
log=$2
echo -n > $LOG0 #Clear no dable
while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $log
  fi
done < $FILE_NAME
sed -i 's/[][]//g' "$log"
}
text_srv="default_name_servers:"
text_lz="default_name_servers_search:"
text_rz="manage_reverse_zones:"
log_rz="$(mktemp)"
log_srv="$(mktemp)"
log_lz="$(mktemp)"

args=(
   "$text_srv" "$log_srv"
   "$text_lz" "$log_lz"
   "$text_rz" "$log_rz"
)

for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done
# cat $log   > $LOG0
#cat $LOG0
###glue

function glue(){
log1=$1
while read line; do
  echo  "Default server ${line}" >> $LOG0
done < $log1

}
glue "$log_srv"
glue "$log_lz"
while read line; do
  echo  "Reverse zone ${line}" >> $LOG0
done < $log_rz
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars5.sh"

else
echo -e "\e[31m######## 4 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars5.sh"

fi

EOF

chmod 775 ./pars4.sh
cat << 'EOF' > ./pars5.sh
#!/bin/bash
echo -e "########\e[31m 5 Настройки файла install_bind9-forward-zone\e[0m########"
FILE_NAME="/var/www/html/stable/astra/1.6/install_bind9-forward-zone"
touch /tmp/log05
LOG0=/tmp/log05

if [ -e "$FILE_NAME" ];then
log_free_="$(mktemp)"


export LOG1=$(grep "\." $log_dns_zg | cut -d"." -f1 ) #Cloud zone export for pars.sh log_dns_zg
grep -A 1 "# $LOG1" $FILE_NAME | sed -n 2p >> $log_free_ #search dns ad
grep "$LOG1." $FILE_NAME >> $log_free_ #search dns Freeipa

function search(){
text=$1
log=$2
echo -n > $LOG0 #Clear no dable
while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $LOG0
  fi
done < $log_free_
sed -i 's/[][]//g' "$log"
sed -i 's/"//g' "$log"      #garbage truck
}
text_ad="="
log_ad="$(mktemp)"
args=(
   "$text_ad" "$log_ad"
)
for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"

done
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars6.sh"
else
echo -e "\e[31m######## 5 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars6.sh"

fi

EOF

chmod 775 ./pars5.sh
cat << 'EOF' > ./pars6.sh
#!/bin/bash
echo -e "########\e[31m 6 Настройки файла install_cinder-volume.ha\e[0m########"
FILE_NAME="/var/www/html/stable/astra/1.6/install_cinder-volume.ha"
LOG0=/tmp/log06
if [ -e "$FILE_NAME" ];then
###
function search(){
text_cr=$1
log_cr=$2

while read line; do
  if [[ "$line" == *"$text_cr"* ]]; then
    echo "${line#*$text_cr}" >> $log_cr
  fi
done < $FILE_NAME
sed -i 's/"//g' "$log_cr"
}

log_c="$(mktemp)"
log_ci="$(mktemp)"
log_cin="$(mktemp)"
text_c="CINDER_VOLUME0_IP="
text_ci="CINDER_VOLUME1_IP="
text_cin="CINDER_VOLUME2_IP="

args=(

   "$text_c" "$log_c"
   "$text_ci" "$log_ci"
   "$text_cin" "$log_cin"
)

for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done

 cat "$log_c" "$log_ci" "$log_cin" > $LOG0

mes="Cinder volume"
log_tmp="$(mktemp)"
while read -r line; do
new_line="$mes $line"
  echo "$new_line" >> "$log_tmp"
done < $LOG0
mv "$log_tmp" "$LOG0"
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars7.sh"
else
echo -e "\e[31m######## 6 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars7.sh"

fi

EOF

chmod 775 ./pars6.sh
cat << 'EOF' > ./pars7.sh
#!/bin/bash
echo -e "########\e[31m 7 Настройки файла named.template\e[0m########"
FILE_NAME="/etc/cobbler/named.template"
LOG0="/tmp/log07"
if [ -e "$FILE_NAME" ];then
text="listen-on port 53 { 127.0.0.1;"
log="$(mktemp)"
while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> "$log"
  fi
sed -i 's/;//g' "$log"      #garbage truck
sed -i 's/}//g' "$log"      #garbage truck
done < $FILE_NAME
####
while read line; do
    echo "Local DNS $line"
done < $log > $LOG0
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars8.sh"

else
echo -e "\e[31m######## 7 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars8.sh"

fi

EOF

chmod 775 ./pars7.sh
cat << 'EOF' > ./pars8.sh
echo -e "########\e[31m 8 Настройки файла keystone.$LOG1.conf\e[0m########"
FILE_NAME="/var/www/html/init/keystone/keystone.$LOG1.conf"
LOG0="/tmp/log08"
if [ -e "$FILE_NAME" ];then
function search(){
text=$1
log_p8=$2
echo -n > $LOG0 #Clear no dable
while read line; do
  if [[ "$line" == *"$text"* && "$line" != *"#"* ]]; then
    echo "${line#*$text}" >> $log_p8
  fi
done < $FILE_NAME
}
text_ur="url ="
text_us="user ="
text_pa="password ="
text_ba="user_tree_dn ="
text_fi="user_filter ="
log_ur="$(mktemp)"
log_us="$(mktemp)"
log_pa="$(mktemp)"
log_ba="$(mktemp)"
log_fi="$(mktemp)"
args=(
   "$text_ur" "$log_ur"
   "$text_us" "$log_us"
   "$text_pa " "$log_pa"
   "$text_ba" "$log_ba"
   "$text_fi" "$log_fi"
)
for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done
cat "$log_ur" "$log_us" "$log_pa" "$log_ba" "$log_fi" >> $LOG0 #Done result
sed -i 's/"//g' "$LOG0"      #garbage truck
sed -i 's/)//g' "$LOG0"      #garbage truck
sed -i 's/(//g' "$LOG0"      #garbage truck

mes="Keystone AD"
log_tmp="$(mktemp)"
while read -r line; do
new_line="$mes $line"
  echo "$new_line" >> "$log_tmp"
done < $LOG0
mv "$log_tmp" "$LOG0"
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars9.sh"
else
echo -e "\e[31m######## 8 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars9.sh"

fi


EOF

chmod 775 ./pars8.sh
cat << 'EOF' > ./pars9.sh
#!/bin/bash
echo -e "########\e[31m 9 Настройки файла keystone.free$LOG1.conf\e[0m########"
FILE_NAME="/var/www/html/init/keystone/keystone.free$LOG1.conf"
LOG0="/tmp/log09"
if [ -e "$FILE_NAME" ];then

function search(){
text=$1
log_p9=$2
echo -n > $LOG0 #Clear no dable
while read line; do
  if [[ "$line" == *"$text"* && "$line" != *"#"* ]]; then
    echo "${line#*$text}" >> $log_p9
  fi
done < $FILE_NAME
}
text_ur="url ="
text_us="user ="
text_pa="password ="
text_ba="user_tree_dn ="
text_fi="user_filter ="
log_ur="$(mktemp)"
log_us="$(mktemp)"
log_pa="$(mktemp)"
log_ba="$(mktemp)"
log_fi="$(mktemp)"
args=(
   "$text_ur" "$log_ur"
   "$text_us" "$log_us"
   "$text_pa " "$log_pa"
   "$text_ba" "$log_ba"
   "$text_fi" "$log_fi"
)
for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done
cat "$log_ur" "$log_us" "$log_pa" "$log_ba" "$log_fi" >> $LOG0 #Done result
sed -i 's/"//g' "$LOG0"      #garbage truck
sed -i 's/)//g' "$LOG0"      #garbage truck
sed -i 's/(//g' "$LOG0"      #garbage truck

#Set messenger
mes="Keystone FreeIpa"
log_tmp="$(mktemp)"
while read -r line; do
new_line="$mes $line"
  echo "$new_line" >> "$log_tmp"
done < $LOG0
mv "$log_tmp" "$LOG0"
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/pars10.sh"
else
echo -e "\e[31m######## 9 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
   source "$set_pwd/pars10.sh"

fi
EOF

chmod 775 ./pars9.sh
cat << 'EOF' > ./pars10.sh
#!/bin/bash

echo -e "########\e[31m 10 Настройки файла zone.template\e[0m########"
FILE_NAME="/etc/cobbler/zone.template"
LOG0="/tmp/log010"

if [ -e "$FILE_NAME" ];then
log="$(mktemp)"
while read line; do
  if [[ "$line" == *"cobbler  "* ]]; then
    echo "${line#*cobbler  }" >> "$log"
  fi
done < $FILE_NAME
sed -i 's/ //g' "$LOG0"      #garbage truck
####
while read line; do
    echo "Variable Cobbler $line"
done < $log > $LOG0
sed -i 's/IN//g' "$LOG0"      #garbage truck
sed -i 's/A//g' "$LOG0"      #garbage truck
source "$set_pwd/greentext.sh"

cat "$LOG0" >> endpars
source "$set_pwd/pars11.sh"

else
echo -e "\e[31m######## 10 No file $FILE_NAME ########\e[0m"
echo -e "No File $FILE_NAME" > "$LOG0"
cat "$LOG0" >> endpars
source "$set_pwd/pars11.sh"


fi

EOF

chmod 775 ./pars10.sh
cat << 'EOF' > ./test.sh
#!/bin/bash
echo -e "########\e[31m  Проверка доступности репозиториев \e[0m########"
filename="/tmp/log0"
log="$(mktemp)"
log2="$(mktemp)"
log3="$(mktemp)"
log4="$(mktemp)"
log5="$(mktemp)"
date=$(date '+%F %T')

urls0=""
while read line
do
  if [[ "$line" == *"pubkey"* ]]; then
    urls0="$urls0 $line"
  fi
done < "$filename"
curl -s -D "$log3" $urls0 > /dev/null #pubkey check
#cat $log3

status_code_key=$(cat "$log3" | head -n1 | tail -n2 | cut -d ' ' -f2)

if [[ $status_code_key = 200 ]]; then
 echo -e "Pubkey \e[32m Done \e[0m \e[33m$date\e[0m"
elif
[ "$status_code_key" = '' ];
then
echo -e "\e[31m Check pach to Pubkey \e[0m \e[33m$date\e[0m"
else
   echo -e "$status_code_key \e[31m No acess to Pubkey \e[0m $urls0 \e[33m$date\e[0m"
fi
###### add simbol
grep "http" "$filename" | awk '{print $1}'| tr -d '\r' > "$log2" #sort repo
sed -i '/pubkey/d' "$log2"

while read line; do
    echo "$line/"
done < "$log2" > "$log"
#######

######## file add
file_prefix="repo_line"
grep -n "http" "$log" | while read -r line; do
  line_number=$(echo "$line" | cut -d: -f1)
  line_text=$(echo "$line" | cut -d: -f2-)

  file_name="${file_prefix}_${line_number}"

   echo "$line_text" > "$file_name"
done

######
function  curl_status(){
repo_path=$1
urls=""
while read line
do
  if [[ "$line" == *"http"* ]]; then
    urls="$urls $line"
  fi
done < "$repo_path"

curl -s -D "$log4" $urls > /dev/null #REPO check

status_code=$(cat "$log4" | head -n1 | tail -n2 | cut -d ' ' -f2)
if [[ $status_code = 200 ]]; then
 echo -e "\e[32mOK \e[0m REPO  \e[33m$date\e[0m"
echo  "OK REPO $date" >> endtest
else
   echo -e "\e[31mERROR \e[0m REPO  $urls \e[33m$date\e[0m"
 echo  "ERROR REPO  $urls $date" >> endtest

fi
}
####
find . -name 'repo_line*' | sed 's|./||; s|/||g' > "$log5" 
while IFS= read -r line; do
  curl_status "$line"
done < "$log5"
source "$set_pwd/endtext.sh"
source "$set_pwd/clear_tmp.sh"

EOF

chmod 775 ./test.sh
cat << 'EOF' > ./greentext.sh
#!/bin/bash
### green text
function greentext() {
while read line; do
  echo -e "\e[32mНайдено значение\e[0m $line"
done < $LOG0
}
greentext

EOF

chmod 775 ./greentext.sh

cat << 'EOF' > ./clear_tmp.sh
#!/bin/bash
function clear_tmp() {

rm /tmp/tmp.*
}
clear_tmp
exit 0
EOF

chmod 775 ./clear_tmp.sh
cat << 'EOF' > ./endtext.sh
#!/bin/bash
date=$(date '+%F %T')
function find_end() {
log=$1
module=$2
  echo 10.40.255.12 | python3 "$module" | tee endtest &
    wait
   # grep 'OK' "$log" | sed -e 's/OK/\x1b[32m&\x1b[0m/g' -e "s/$/ \x1b[33m$date\x1b[0m/"
    #  grep 'ERROR' "$log" | sed -e 's/ERROR/\x1b[31m&\x1b[0m/g' -e "s/$/ \x1b[33m$date\x1b[0m/"
}
args=(

"/tmp/log_test" "/$set_pwd/custom_checks/parse.py"

)

for (( i=0; i<${#args[@]}; i+=2 )); do
  find_end "${args[i]}" "${args[i+1]}"
done
EOF

chmod 775 ./endtext.sh
cat << 'EOF' > ./check_pack.sh
#!/bin/bash

check_package() {
    if dpkg -s "$1" >/dev/null 2>&1; then
        echo -e " \e[32mOK \e[0m Package $1 is installed."
    else
        echo -e "\e[31mERROR \e[0m Package $1 is not installed."
    fi
}

check_package "curl"
check_package "ldap-utils"
check_package "isc-dhcp-client"
source /root/custom_checks/venv/bin/activate
EOF

chmod 775 ./check_pack.sh

cat << 'EOF' > ./pars11.sh
#!/bin/bash
echo -e "########\e[31m 11 Настройки файла san.cfg \e[0m########"
LOG0=/tmp/log11
FILE_NAME="/var/www/html/stable/astra/1.6/san.cfg"
if [ -e "$FILE_NAME" ];then
###
function search(){
text=$1
log=$2
echo -n > $log
while read line; do
  if [[ "$line" == *"$text"* ]]; then
    echo "${line#*$text}" >> $log
  fi
done < $FILE_NAME
sed -i 's/"//g' $log
}

log_san=/tmp/log11_1

text_san="server "

args=(
   "$text_san" "$log_san"
)

for (( i=0; i<${#args[@]}; i+=2 )); do
  search "${args[i]}" "${args[i+1]}"
done

### IP SAN
echo -n > "$LOG0"
regex="([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
while read -r line; do
    if [[ "$line" =~ $regex ]]; then
        ip="${BASH_REMATCH[1]}"
        echo -e "SAN $ip" >> "$LOG0"
    fi
done < "$log_san"
cat "$LOG0" >> endpars
source "$set_pwd/greentext.sh"
source "$set_pwd/test.sh"
source "$set_pwd/clear_tmp.sh"

else

echo -e "\e[31m 1 No file $FILE_NAME \e[0m"
echo -e "No File" > "$LOG0"
cat "$LOG0" >> endpars
source "$set_pwd/test.sh"
source "$set_pwd/clear_tmp.sh"

fi

EOF

chmod 775 ./pars11.sh

cat << 'EOF' > ./ini.sh
#!/bin/bash
echo -e -n "Введите номер версии для ОС Астра: 1-(1.6) или 2-(1.7) \n"
read -r pa_os

if [ "$pa_os" = 1 ]; then
   source <(grep = 16.ini | sed 's/ *= */=/g')
    elif [ "$pa_os" = 2 ]; then
     source <(grep = 17.ini | sed 's/ *= */=/g')


 else
  echo "Нет верных данных повторите запуск"
   exit 0
fi

EOF

chmod 775 ./ini.sh

cat << 'EOF' > ./16.ini
[16]
pars=/var/www/html/stable/astra/1.6/initrc_
pars2=/var/www/html/stable/astra/1.6/initrc_2
EOF

cat << 'EOF' > ./17.ini
[17]
pars=/var/www/html/stable/astra/1.7/initrc_
pars2=/var/www/html/stable/astra/1.7/initrc_2
EOF
source pars.sh