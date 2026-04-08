/* 05_graphs.sas */
/* Etapa 5: generarea de grafice */

options validvarname=any;
options fmtsearch=(proj work);
ods graphics on;

%let root=/home/u64494277/pachete_software_sas;
libname proj "&root/sasdata";

/* =========================================================
   1. Seturi agregate pentru grafice
========================================================= */

/* 1a. Sinteza anuala */
proc sql;
    create table work.year_graph as
    select
        year format=4.,
        sum(traffic) as total_traffic format=comma15.,
        sum(total_delay) as total_delay format=comma15.,
        mean(avg_delay_per_flight) as mean_delay_per_flight format=8.4
    from proj.analysis_dataset
    group by year
    order by year;
quit;

/* 1b. Evolutie lunara pe intreaga perioada */
proc sql;
    create table work.month_graph as
    select
        intnx('month', FLT_DATE, 0, 'b') as month_date format=monyy7.,
        year format=4.,
        month format=2.,
        sum(traffic) as total_traffic format=comma15.,
        sum(total_delay) as total_delay format=comma15.,
        mean(avg_delay_per_flight) as mean_delay_per_flight format=8.4
    from proj.analysis_dataset
    group by calculated month_date, year, month
    order by calculated month_date;
quit;

/* 1c. Medii pe perioade */
proc sql;
    create table work.period_graph as
    select
        case
            when period_label = 'Pre-COVID' then 1
            when period_label = 'COVID' then 2
            when period_label = 'Post-COVID' then 3
            else .
        end as period_order,
        period_label,
        mean(traffic) as mean_traffic format=8.2,
        mean(total_delay) as mean_total_delay format=8.2,
        mean(avg_delay_per_flight) as mean_delay_per_flight format=8.4
    from proj.analysis_dataset
    group by period_label
    order by period_order;
quit;

/* 1d. Distributia clusterelor */
proc sql;
    create table work.cluster_counts as
    select
        cluster,
        count(*) as n_airports format=comma10.
    from proj.airport_cluster_profile
    group by cluster
    order by cluster;
quit;

/* 1e. Top 15 aeroporturi dupa trafic total */
proc sql;
    create table work.airport_rank_traffic as
    select
        APT_ICAO,
        STATE_NAME,
        cluster,
        total_traffic,
        total_delay,
        mean_traffic,
        mean_total_delay
    from proj.airport_cluster_profile
    order by total_traffic desc;
quit;

data work.top15_airports_traffic;
    set work.airport_rank_traffic(obs=15);
    length airport_label $40;
    airport_label = catx(' - ', strip(APT_ICAO), strip(STATE_NAME));
run;

/* 1f. Top 15 aeroporturi dupa intarziere totala */
proc sql;
    create table work.airport_rank_delay as
    select
        APT_ICAO,
        STATE_NAME,
        cluster,
        total_traffic,
        total_delay,
        mean_traffic,
        mean_total_delay
    from proj.airport_cluster_profile
    order by total_delay desc;
quit;

data work.top15_airports_delay;
    set work.airport_rank_delay(obs=15);
    length airport_label $40;
    airport_label = catx(' - ', strip(APT_ICAO), strip(STATE_NAME));
run;

/* =========================================================
   2. Grafice anuale
========================================================= */

title "Grafic 1. Trafic total anual";
proc sgplot data=work.year_graph;
    vbarparm category=year response=total_traffic / datalabel;
    xaxis label="An" integer;
    yaxis label="Trafic total";
run;

title "Grafic 2. Intarziere totala anuala";
proc sgplot data=work.year_graph;
    vbarparm category=year response=total_delay / datalabel;
    xaxis label="An" integer;
    yaxis label="Intarziere totala";
run;

title "Grafic 3. Intarziere medie per zbor pe ani";
proc sgplot data=work.year_graph;
    series x=year y=mean_delay_per_flight / markers lineattrs=(thickness=2);
    xaxis label="An" integer;
    yaxis label="Intarziere medie per zbor";
run;

/* =========================================================
   3. Grafice de evolutie lunara
========================================================= */

title "Grafic 4. Evolutia lunara a traficului total";
proc sgplot data=work.month_graph;
    series x=month_date y=total_traffic / markers lineattrs=(thickness=2);
    xaxis label="Luna" fitpolicy=rotate;
    yaxis label="Trafic total lunar";
run;

title "Grafic 5. Evolutia lunara a intarzierii totale";
proc sgplot data=work.month_graph;
    series x=month_date y=total_delay / markers lineattrs=(thickness=2);
    xaxis label="Luna" fitpolicy=rotate;
    yaxis label="Intarziere totala lunara";
run;

/* 3b. Panel: trafic lunar pe ani, fiecare an in panou separat */
title "Grafic 5b. Trafic lunar pe ani (panouri)";
proc sgpanel data=work.month_graph;
    panelby year / layout=columnlattice columns=5 novarname;
    vbar month / response=total_traffic stat=sum;
    colaxis label="Luna" fitpolicy=thin;
    rowaxis label="Trafic total";
run;

/* =========================================================
   4. Grafice comparative pe perioade
========================================================= */

title "Grafic 6. Media traficului pe perioade";
proc sgplot data=work.period_graph;
    vbarparm category=period_label response=mean_traffic / datalabel;
    xaxis label="Perioada" discreteorder=data;
    yaxis label="Media traficului";
run;

title "Grafic 7. Media intarzierii totale pe perioade";
proc sgplot data=work.period_graph;
    vbarparm category=period_label response=mean_total_delay / datalabel;
    xaxis label="Perioada" discreteorder=data;
    yaxis label="Media intarzierii totale";
run;

title "Grafic 8. Media intarzierii per zbor pe perioade";
proc sgplot data=work.period_graph;
    vbarparm category=period_label response=mean_delay_per_flight / datalabel;
    xaxis label="Perioada" discreteorder=data;
    yaxis label="Media intarzierii per zbor";
run;

/* 4b. Boxplot: distributia traficului pe perioade */
title "Grafic 8b. Distributia traficului pe perioade (boxplot)";
proc sgplot data=proj.analysis_dataset;
    vbox traffic / category=period_label;
    xaxis label="Perioada";
    yaxis label="Trafic zilnic";
run;

/* =========================================================
   5. Grafice pentru clustering
========================================================= */

title "Grafic 9. Distributia aeroporturilor pe clustere";
proc sgplot data=work.cluster_counts;
    vbarparm category=cluster response=n_airports / datalabel;
    xaxis label="Cluster";
    yaxis label="Numar aeroporturi";
run;

title "Grafic 10. Clustering al aeroporturilor in functie de trafic si intarzieri";
proc sgplot data=proj.airport_cluster_profile;
    scatter x=mean_traffic y=mean_total_delay / group=cluster transparency=0.15;
    xaxis label="Trafic mediu zilnic";
    yaxis label="Intarziere medie zilnica";
run;

/* =========================================================
   6. Grafice pentru top aeroporturi
========================================================= */

title "Grafic 11. Top 15 aeroporturi dupa trafic total";
proc sgplot data=work.top15_airports_traffic;
    hbarparm category=airport_label response=total_traffic /
        datalabel
        group=cluster
        groupdisplay=cluster;
    xaxis label="Trafic total";
    yaxis label="Aeroport" discreteorder=data reverse;
run;

title "Grafic 12. Top 15 aeroporturi dupa intarziere totala";
proc sgplot data=work.top15_airports_delay;
    hbarparm category=airport_label response=total_delay /
        datalabel
        group=cluster
        groupdisplay=cluster;
    xaxis label="Intarziere totala";
    yaxis label="Aeroport" discreteorder=data reverse;
run;

title;
ods graphics off;