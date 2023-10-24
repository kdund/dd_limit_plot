for file in ./*.csv
do
    vim -c "%s/,,\|  /,/g" -c "wq" "${file}"
done
