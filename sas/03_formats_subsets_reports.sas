/* 03_formats_subsets_reports.sas */
/* Etapa 3: formate definite de utilizator, subseturi si rapoarte */

options validvarname=any;
options fmtsearch=(proj work);

%let root=/home/u64494277/pachete_software_sas;
libname proj "&root/sasdata";

/* 1. Crearea formatelor definite de utilizator */
proc format library=proj;
    value yeargrp
        2019        = 'Pre-COVID'
        2020, 2021  = 'COVID'
        2022, 2023  = 'Post-COVID';

    value trafficfmt
        low - <50   = 'Trafic foarte redus'
        50 - <150   = 'Trafic redus-mediu'
        150 - <300  = 'Trafic ridicat'
        300 - high  = 'Trafic foarte ridicat';

    value delayfmt
        0           = 'Fara intarzieri'
        0 <- 30     = 'Intarzieri reduse'
        30 <- 120   = 'Intarzieri moderate'
        120 - high  = 'Intarzieri mari';
run;

/* 2. Crearea setului de analiza */
data proj.analysis_dataset;
    set proj.final_dataset;

    length period_label $12 traffic_category $25 delay_category $22;

    period_label     = put(year, yeargrp.);
    traffic_category = put(traffic, trafficfmt.);
    delay_category   = put(total_delay, delayfmt.);

    if traffic > 0 then avg_delay_per_flight = total_delay / traffic;
    else avg_delay_per_flight = .;

    label
        period_label         = "Perioada de analiza"
        traffic_category     = "Categorie trafic"
        delay_category       = "Categorie intarziere"
        avg_delay_per_flight = "Intarziere medie per zbor";
run;

/* 3. Crearea de subseturi tematice */
data proj.pre_covid
     proj.covid_period
     proj.post_covid_period;
    set proj.analysis_dataset;

    if year = 2019 then output proj.pre_covid;
    else if year in (2020, 2021) then output proj.covid_period;
    else if year in (2022, 2023) then output proj.post_covid_period;
run;

/* 4. Raport 1 - distributia observatiilor pe perioada */
title "Distributia observatiilor pe perioade";
proc freq data=proj.analysis_dataset;
    tables period_label / nocum;
run;

/* 5. Raport 2 - distributia categoriilor de trafic */
title "Distributia observatiilor pe categorii de trafic";
proc freq data=proj.analysis_dataset;
    tables traffic_category / nocum;
run;

/* 6. Raport 3 - distributia categoriilor de intarziere */
title "Distributia observatiilor pe categorii de intarziere";
proc freq data=proj.analysis_dataset;
    tables delay_category / nocum;
run;

/* 7. Raport 4 - tabel de contingenta perioada x categorie trafic */
title "Perioada de analiza versus categoria de trafic";
proc freq data=proj.analysis_dataset;
    tables period_label * traffic_category / norow nocol nopercent;
run;

/* 8. Raport agregat pe tari - top 15 tari dupa traficul total */
proc sql outobs=15;
    create table work.top15_countries as
    select
        STATE_NAME,
        sum(traffic) as total_traffic format=comma15.,
        sum(total_delay) as total_delay format=comma15.,
        case
            when sum(traffic) > 0 then sum(total_delay) / sum(traffic)
            else .
        end as avg_delay_per_flight format=8.2
    from proj.analysis_dataset
    group by STATE_NAME
    order by calculated total_traffic desc;
quit;

title "Top 15 tari dupa traficul total";
proc report data=work.top15_countries nowd;
    columns STATE_NAME total_traffic total_delay avg_delay_per_flight;

    define STATE_NAME / display "Tara";
    define total_traffic / display "Trafic total" format=comma15.;
    define total_delay / display "Intarziere totala" format=comma15.;
    define avg_delay_per_flight / display "Intarziere medie / zbor";
run;

/* 9. Raport agregat pe ani */
proc sql;
    create table work.year_summary as
    select
        year,
        put(year, yeargrp.) as period_label length=12,
        sum(traffic) as total_traffic format=comma15.,
        sum(total_delay) as total_delay format=comma15.,
        case
            when sum(traffic) > 0 then sum(total_delay) / sum(traffic)
            else .
        end as avg_delay_per_flight format=8.2
    from proj.analysis_dataset
    group by year
    order by year;
quit;

title "Sinteza anuala a traficului si intarzierilor";
proc report data=work.year_summary nowd;
    columns year period_label total_traffic total_delay avg_delay_per_flight;

    define year / display "An";
    define period_label / display "Perioada";
    define total_traffic / display "Trafic total" format=comma15.;
    define total_delay / display "Intarziere totala" format=comma15.;
    define avg_delay_per_flight / display "Intarziere medie / zbor";
run;

/* 10. Verificari finale */
title "Numar observatii in seturile create la etapa 3";
proc sql;
    select "ANALYSIS_DATASET" as tabel length=20, count(*) as observatii
    from proj.analysis_dataset

    union all

    select "PRE_COVID" as tabel length=20, count(*) as observatii
    from proj.pre_covid

    union all

    select "COVID_PERIOD" as tabel length=20, count(*) as observatii
    from proj.covid_period

    union all

    select "POST_COVID_PERIOD" as tabel length=20, count(*) as observatii
    from proj.post_covid_period;
quit;

title "Primele 10 observatii din ANALYSIS_DATASET";
proc print data=proj.analysis_dataset(obs=10) noobs;
    var FLT_DATE APT_ICAO STATE_NAME traffic total_delay period_label traffic_category delay_category avg_delay_per_flight;
run;

title;