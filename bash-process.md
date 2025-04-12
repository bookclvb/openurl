# Bash OpenURL creation process

First I export bibliographic records that need an OpenURL from the ILS.
I am using 3 records in this example. This is structured MARC that exports into a .mrc file. 
I then run them through a program called MarcEdit to make them human-readable. They export into a .mrk file (let’s call it “test.mrk”). Here is what that output for the three .mrk records looks like:
```
=LDR  01454pam a2200337 a 4500
=001  10482998
=003  dti
=005  19980825093807.0
=008  840215s1984\\\\nyua\\\\\\\\\\000\0\eng\\
=010  \\$a84003773
=020  \\$a0517554240 (pbk.)
=035  \\$aRISD    59789
=040  \\$aDLC$cDLC$dRSD
=049  \\$aRSDb
=099  \\$aH225A
=100  1\$aHaring, Keith.
=245  10$aArt in transit :$bsubway drawings /$cby Keith Haring ; photos by Tseng Kwong Chi ; introduction by Henry Geldzahler ; design by Dan Friedman.
=250  \\$a1st ed.
=260  \\$aNew York :$bHarmony Books,$cc1984.
=300  \\$a[96] pages :$bchiefly color illustrations ;$c30 cm.
=600  10$aHaring, Keith.
=650  \0$aSubways$xDecoration.
=650  \0$aArtists' books$zUnited States.
=700  1\$aTseng, Kwong Chi.
=700  1\$aFriedman, Dan.
=907  \\$a.b10574141$brabg $cl
=902  \\$a240723
=998  \\$b1$c970101$dm$ea  $fl$g0
=902  \\$g1$t4$l071114$k11-14-2007 16:46
=945  \\$lrabg $u4$v0$y.i10656601$z980908$so  $h0$q $r-$i24444000308009

=LDR  01585nam a2200325Mi 4500
=001  26825868
=003  dti
=005  19980825093820.0
=008  921008s1970\\\\nyua\\\\\\\\\\000\0\eng\d
=035  \\$aRISD    60397
=040  \\$aTEU$cTEU$dRSD
=043  \\$an-us---
=049  \\$aRSDb
=099  \\$aK14P
=100  1\$aKaprow, Allan.
=245  10$aPose :$bcarrying chairs through the city, sitting down here and there, photographed, pix left on spot, going on /$c[Allan Kaprow].
=260  \\$aN.Y. [i.e. New York, N.Y.] :$bMultiples,$cc1970.
=300  \\$a7 leaves of plates :$billus. ;$c28 cm.
=500  \\$aAbove title on first leaf: March 22.
=500  \\$aNote on envelope : "Occured in and around Berkeley, California, March 22, 23, 1969."
=500  \\$aSeven plates in envelope (31 cm)
=500  \\$aThis project was part of the "Artists and photographers" box set published: New York: Multiples, 1970.
=650  \0$aArtists' books$zUnited States.
=710  2\$aMultiples, Inc. (Art publisher)
=907  \\$a.b10580220$brabg $cl
=902  \\$a250123
=998  \\$b1$c970101$dm$ea  $fl$g0
=902  \\$g1$t4$l150922$k09-22-2015 14:14
=945  \\$lrabg $u2$v0$y.i10663368$z980908$so  $h0$q $r-$i24444000314528

=LDR  01891cam a2200349Ia 4500
=001  903592749
=003  OCoLC
=005  20160329112715.0
=008  150218s2014\\\\nyua\\\\\\\\\\000\0\eng\d
=035  \\$a(OCoLC)903592749
=040  \\$aFNE$beng$cFNE$dOCLCF$dOCLCQ$dRSD
=049  \\$aRSDg
=099  \\$aAu37ZH
=100  1\$aAuerbach, Tauba,$d1981-
=245  10$aZ Helix /$cTauba Auerbach.
=264  \1$aNew York :$bDiagonal Press,$c2014.
=300  \\$a116 pages :$ball illustrated ;$c27 cm
=336  \\$astill image$bsti$2rdacontent
=336  \\$atext$btxt$2rdacontent
=337  \\$aunmediated$bn$2rdamedia
=338  \\$avolume$bnc$2rdacarrier
=500  \\$a"The helix is chiral and exists in two varieties, S and Z.  The book Z Helix developed around the manufacturing conventions of coil bindings (which are only available as Z helices), and the color and structure of the sculpture 'Square Helix (Z)' which was included in an exhibition entitled The New Ambidextrous Universe at the ICA London in 2014. The book contains five Z helices"--Insert.
=500  \\$aTwo color coils interweaved. Spiral bindings in orange and blue.  Indigo print on 4mm transparency film.
=500  \\$aHoused in a corrugated cardboard box (31 x 26 cm)  Title, author and imprint info stamped with a custom rubber stamp on container.
=650  \0$aArtists' books.
=650  \0$aHelices (Algebraic topology)$vIn art.
=907  \\$a.b14596994$brabg $c 
=902  \\$a240723
=998  \\$b1$c160329$dm$ea  $f $g0
=902  \\$g1$t4$l220311$k03-11-2022 14:41
=945  \\$lrabg $u31$v0$y.i13538949$z160329$so  $h0$q $r $i24444001480641
```

Next, I export a .txt file (let’s call it “bib.txt”)  from the library system that includes just the details I want to use in the OpenURLs. Here’s what it looks like:
```
RECORD #(BIBLIO)|AUTHOR|TITLE|ADD TITLE|CALL #(BIBLIO)|MAT TYPE|LOCATION
b10574141|Haring, Keith.|Art in transit : subway drawings / by Keith Haring   photos by Tseng Kwong Chi   introduction by Henry Geldzahler   design by Dan Friedman.||H225A|a  |rabg 
b10580220|Kaprow, Allan.|Pose : carrying chairs through the city, sitting down here and there, photographed, pix left on spot, going on / [Allan Kaprow].||K14P|a  |rabg 
b14596994|Auerbach, Tauba, 1981-|Z Helix / Tauba Auerbach.||Au37ZH|a  |rabg 
```
I open this file and delete the first line headers (“RECORD #(BIBLIO)|AUTHOR|TITLE|ADD TITLE|CALL #(BIBLIO)|MAT TYPE|LOCATION”).
I place these two files “test.mrk” and “bib.txt” into the folder with my .sh scripts. There is also a file in this folder called “locations.txt” that my scripts reference. 
I run my first script to build the OpenURLs:
```
#!/bin/bash
#
echo "Script started"


# Pull values into variables from bib.txt
while read line
do
    bibnum=$(echo $line | cut -d'|' -f1)
    blink=$(echo $bibnum | sed 's/[0-9a-z]$//g')
    author=$(echo $line | cut -d'|' -f2 | sed 's/&/%26/g' | sed 's/+/%2b/g' | sed 's/ /+/g')
    title_a=$(echo $line | cut -d'|' -f3 | sed 's/&/%26/g' | sed 's/+/%2b/g' | sed 's/ /+/g')
    title_b=$(echo $line | cut -d'|' -f4 | sed 's/&/%26/g' | sed 's/+/%2b/g' | sed 's/ /+/g')
    callnum=$(echo $line | cut -d'|' -f5 | sed 's/&/%26/g' | sed 's/+/%2b/g' | sed 's/ /+/g')
    genre_raw=$(echo $line | cut -d"|" -f6 | tr -d ' ')
    loc_code=$(echo $line | cut -d'|' -f7)
#
# concatenate titles, add placeholder if no call number


x_title=$(echo "$title_a $title_b")


if [ -z "$author" ];then
    x_author=$(echo "BLANK")
else
    x_author=$(echo $author)
fi


if [ -z "$callnum" ];then
    x_callnum=$(echo "n/a")
else
    x_callnum=$(echo $callnum)
fi


# Initialize default values, including blanking out unusual variables
genre="monograph"
volume="BLANK"
i_title="BLANK"
s_title="BLANK"


# Send periodicals and archival materials to the appropriate request form
# Set "n/a" placeholder for serial volume and manuscript box number


if [[ "$genre_raw" == "x" ]]; then
    genre="serial"
    volume="n/a"
elif [[ "$genre_raw" == "b" ]]; then
    genre="manuscript"
    volume="n/a"
    i_title=$(echo $x_title)
    x_title="BLANK"
fi




# use this line for archives, otherwise comment out and use the if statement below
# location="RISD Archives"


# if multiple loc_code, set location to Multiple and match descriptive location accordingly
# it may be possible to make this concatenate and list multiple locations, but not today, satan!


if echo "$loc_code" | grep -q ','; then
  location="Multiple"
else
  location=$(grep ^$loc_code\| "locations.txt" | cut -d'|' -f2 | sed 's/ /+/g')
fi




#BUILD URLS
baseurl=$(echo "https://aeon.risd.edu/logon?Action=10&Form=30&")
permalink=$(echo "https://librarycat.risd.edu/record="$blink)
url_raw=$(echo $baseurl"Genre="$genre"&Title="$x_title"&ItemTitle="$i_title"&ItemSubTitle="$s_title"&Author="$x_author"&CallNumber="$x_callnum"&ItemVolume="$volume"&Location="$location"&ItemInfo1="$permalink)
finalurl=$(echo $url_raw | sed 's/&Title=BLANK//g' | sed 's/&ItemTitle=BLANK//g' | sed 's/&ItemSubTitle=BLANK//g' | sed 's/&Author=BLANK//g' | sed 's/&ItemVolume=BLANK//g' | sed 's/&Location=BLANK//g' | sed 's/ /+/g')
#
echo $bibnum'|'$finalurl >> urls.txt
done < bib.txt
echo "Script ended"
```
I check this file to be sure the OpenURLs work.
I run my second script:
```
#!/bin/bash
#
echo "Script started"
# grep '=LDR\|=245\|=907\|^$' test.mrk | tr '\n' '^' > extract.txt
grep '=LDR\|=245\|=907\|^$' test.mrk | tr '\n' '^' | sed 's/\^\^/^/g' > extract.txt
# grep '=LDR\|=245\|=907\|^$' test.mrk | tr -d '\n|^' | sed 's/=LDR/\n=LDR/g' > extract.txt
echo "Script ended. Check extract.txt for results"
```
I check this file to make sure it looks the way I want. This step tends to be troublesome (Command Prompt and Terminal seem to parse it differently).

The extract.txt file should look something like this: 
```
=LDR  01454pam a2200337 a 4500^=245  10$aArt in transit :$bsubway drawings /$cby Keith Haring ; photos by Tseng Kwong Chi ; introduction by Henry Geldzahler ; design by Dan Friedman.^=907  \\$a.b10574141$brabg $cl

=LDR  01585nam a2200325Mi 4500^=245  10$aPose :$bcarrying chairs through the city, sitting down here and there, photographed, pix left on spot, going on /$c[Allan Kaprow].^=907  \\$a.b10580220$brabg $cl

=LDR  01891cam a2200349Ia 4500^=245  10$aZ Helix /$cTauba Auerbach.^=907  \\$a.b14596994$brabg $c 
```
The final script combines extract.txt and the OpenURLs into a new file:
```
#!/bin/bash
#
echo "Script started"
while read line
do
bnum=$(echo $line | cut -d"|" -f1)
url=$(echo $line | cut -d"|" -f2)
url_insert=$(echo "=856  40\$u"$url\$"zSpecial Collections Request")
record=$(grep $bnum extract.txt)
echo "$record" | grep -v ^$ >> done.txt
# echo "$record" | tr "\^" "\012" | grep -v ^$ >> done.txt
echo "$url_insert" >> done.txt
echo >> done.txt
done < urls.txt
echo "Script ended. Check done.txt for results"
```

This should result in a file that looks like so:
```
=LDR  01454pam a2200337 a 4500
=245  10$aArt in transit :$bsubway drawings /$cby Keith Haring ; photos by Tseng Kwong Chi ; introduction by Henry Geldzahler ; design by Dan Friedman.
=907  \\$a.b10574141$brabg $cl
=856  40$uhttps://aeon.risd.edu/logon?Action=10&Form=30&Genre=monograph&Title=Art+in+transit+:+subway+drawings+/+by+Keith+Haring+photos+by+Tseng+Kwong+Chi+introduction+by+Henry+Geldzahler+design+by+Dan+Friedman.+&Author=Haring,+Keith.&CallNumber=H225A&Location=RISD+Artists+Books+Oversize&ItemInfo1=https://librarycat.risd.edu/record=b1057414$zSpecial Collections Request

=LDR  01585nam a2200325Mi 4500
=245  10$aPose :$bcarrying chairs through the city, sitting down here and there, photographed, pix left on spot, going on /$c[Allan Kaprow].
=907  \\$a.b14596994$brabg $c 
=856  40$uhttps://aeon.risd.edu/logon?Action=10&Form=30&Genre=monograph&Title=Pose+:+carrying+chairs+through+the+city,+sitting+down+here+and+there,+photographed,+pix+left+on+spot,+going+on+/+[Allan+Kaprow].+&Author=Kaprow,+Allan.&CallNumber=K14P&Location=RISD+Artists+Books+Oversize&ItemInfo1=https://librarycat.risd.edu/record=b1058022$zSpecial Collections Request

=LDR  01891cam a2200349Ia 4500
=245  10$aZ Helix /$cTauba Auerbach.
=907  \\$a.b14596994$brabg $c 
=856  40$uhttps://aeon.risd.edu/logon?Action=10&Form=30&Genre=monograph&Title=Z+Helix/+Tauba+Auerbach.+&Author=Auerbach,+Tauba.&CallNumber=Au37ZH&Location=RISD+Artists+Books+Oversize&ItemInfo1=https://librarycat.risd.edu/record=b1459699$zSpecial Collections Request
```
I then open this txt file as an .mrk file and convert it to .mrc MARC using MARCedit. Then it can be ingested into Sierra and overlaid into the existing bib records.



