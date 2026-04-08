/* 01_import_raw.sas */
/* Etapa 1: importul fisierelor CSV raw in seturi SAS permanente */

options validvarname=any;

%let root=/home/u64494277/pachete_software_sas;

/* biblioteca permanenta pentru seturile SAS */
libname proj "&root/sasdata";

/* macro de import pentru fisiere cu ani consecutivi */
%macro import_series(prefix=, start_year=2019, end_year=2023);

    %do an=&start_year %to &end_year;

        %put NOTE: ==== Import fisier &prefix._&an..csv ====;

        proc import
            datafile="&root/raw/&prefix._&an..csv"
            out=proj.&prefix._&an
            dbms=csv
            replace;
            getnames=yes;
            guessingrows=max;
        run;

    %end;

%mend;

/* import trafic */
%import_series(prefix=airport_traffic);

/* import intarzieri */
%import_series(prefix=apt_dly);

/* verificare 1: lista tabelelor importate */
title "Tabele importate in biblioteca PROJ";
proc datasets lib=proj;
quit;

/* verificare 2: structura seturilor */
title "Structura setului airport_traffic_2019";
proc contents data=proj.airport_traffic_2019 varnum;
run;

title "Structura setului apt_dly_2019";
proc contents data=proj.apt_dly_2019 varnum;
run;

/* verificare 3: primele observatii - dovada vizuala ca importul a functionat */
title "Primele 5 observatii - airport_traffic_2019";
proc print data=proj.airport_traffic_2019(obs=5) noobs;
run;

title "Primele 5 observatii - apt_dly_2019";
proc print data=proj.apt_dly_2019(obs=5) noobs;
run;

/* verificare 4: numar observatii per tabel importat */
title "Numar observatii per tabel importat";
proc sql;
    select memname as Tabel,
           nobs as Observatii
    from dictionary.tables
    where libname = 'PROJ'
      and memtype = 'DATA'
    order by memname;
quit;

title;