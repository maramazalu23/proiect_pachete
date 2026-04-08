/* 04_statistical_procedures.sas */
/* Etapa 4: proceduri statistice */

options validvarname=any;
options fmtsearch=(proj work);
ods graphics on;

%let root=/home/u64494277/pachete_software_sas;
libname proj "&root/sasdata";

/* 1. Sortare doar pentru procedurile care folosesc BY */
proc sort data=proj.analysis_dataset
          out=work.analysis_sorted;
    by period_label;
run;

/* 2. Statistici descriptive generale */
title "Statistici descriptive generale";
proc means data=proj.analysis_dataset
           n nmiss mean median std min q1 q3 max maxdec=2;
    var traffic total_delay avg_delay_per_flight;
run;

/* 3. Statistici descriptive pe perioade */
/* CLASS nu necesita sortare */
title "Statistici descriptive pe perioada de analiza";
proc means data=proj.analysis_dataset
           n mean median std min max maxdec=2;
    class period_label;
    var traffic total_delay avg_delay_per_flight;
run;

/* 4. Statistici descriptive pe ani */
title "Statistici descriptive pe ani";
proc means data=proj.analysis_dataset
           n mean median std min max maxdec=2;
    class year;
    var traffic total_delay avg_delay_per_flight;
run;

/* 5. Distributii + histograme */
ods select Moments BasicMeasures Histogram;

title "Distributia variabilei TRAFFIC";
proc univariate data=proj.analysis_dataset;
    var traffic;
    histogram traffic / normal;
    inset n mean median std min max / position=ne;
run;

title "Distributia variabilei TOTAL_DELAY";
proc univariate data=proj.analysis_dataset;
    var total_delay;
    histogram total_delay / normal;
    inset n mean median std min max / position=ne;
run;

title "Distributia variabilei AVG_DELAY_PER_FLIGHT";
proc univariate data=proj.analysis_dataset;
    var avg_delay_per_flight;
    histogram avg_delay_per_flight / normal;
    inset n mean median std min max / position=ne;
run;

ods select all;

/* 6. Corelatii generale */
title "Matricea de corelatie pentru variabilele principale";
proc corr data=proj.analysis_dataset pearson nosimple;
    var traffic total_delay avg_delay_per_flight year month;
run;

/* 7. Corelatii pe perioada */
/* aici BY cere sortare */
title "Corelatia dintre traffic si total_delay pe perioade";
proc corr data=work.analysis_sorted pearson nosimple;
    by period_label;
    var traffic total_delay avg_delay_per_flight;
run;

/* 8. Regresie liniara simpla */
/* oprim ploturile implicite, ca sa nu mai apara warning-ul cu >5000 puncte */
ods select ANOVA ParameterEstimates FitStatistics;
title "Regresie liniara simpla: total_delay in functie de traffic";
proc reg data=proj.analysis_dataset plots=none;
    model total_delay = traffic;
quit;
ods select all;

/* 9. Regresie pe perioade */
/* RSQUARE adauga _RSQ_ in OUTEST */
title "Regresie liniara pe perioade: total_delay in functie de traffic";
proc reg data=work.analysis_sorted
         outest=work.reg_by_period
         rsquare
         noprint;
    by period_label;
    model total_delay = traffic;
quit;

title "Coeficienti regresie pe perioade";
proc print data=work.reg_by_period noobs;
    var period_label _TYPE_ _DEPVAR_ Intercept traffic _RSQ_;
run;

/* 10. Tabel sinteza statistica pe perioade */
proc sql;
    create table work.period_summary_stats as
    select
        period_label,
        count(*) as n_obs format=comma12.,
        mean(traffic) as mean_traffic format=8.2,
        mean(total_delay) as mean_total_delay format=8.2,
        mean(avg_delay_per_flight) as mean_delay_per_flight format=8.4,
        median(traffic) as median_traffic format=8.2,
        median(total_delay) as median_total_delay format=8.2
    from proj.analysis_dataset
    group by period_label
    order by period_label;
quit;

title "Sinteza statistica pe perioade";
proc report data=work.period_summary_stats nowd;
    columns period_label n_obs mean_traffic mean_total_delay mean_delay_per_flight
            median_traffic median_total_delay;

    define period_label / display "Perioada";
    define n_obs / display "Nr. observatii";
    define mean_traffic / display "Media trafic";
    define mean_total_delay / display "Media intarziere totala";
    define mean_delay_per_flight / display "Media intarziere / zbor";
    define median_traffic / display "Mediana trafic";
    define median_total_delay / display "Mediana intarziere";
run;

/* ====================================================================
   10b. PROC TABULATE - Sinteza multidimensionala (Pivot Table)
   Demonstram stapanirea mai multor proceduri de raportare (Cerinta 8)
==================================================================== */
title "Tabel multidimensional: Trafic si Intarzieri pe Perioade si Categorii";

proc tabulate data=proj.analysis_dataset missing;
    class period_label traffic_category;
    var traffic total_delay;
    
    keylabel sum="Total" mean="Media";
    
    table period_label='Perioada' ALL='Total General',
          traffic_category='Categoria de Trafic' *
          (traffic='Trafic' total_delay='Intarzieri') *
          (sum=''*f=comma15. mean=''*f=8.2)
          / rts=25 box="Indicatori";
run;
title;

/* 11. Baza pentru clustering K-Means la nivel de aeroport */
proc sql;
    create table work.airport_cluster_base as
    select
        APT_ICAO,
        STATE_NAME,
        count(*) as n_days format=comma10.,
        mean(traffic) as mean_traffic format=8.2,
        mean(total_delay) as mean_total_delay format=8.2,
        mean(avg_delay_per_flight) as mean_delay_per_flight format=8.4,
        sum(traffic) as total_traffic format=comma15.,
        sum(total_delay) as total_delay format=comma15.
    from proj.analysis_dataset
    group by APT_ICAO, STATE_NAME
    order by APT_ICAO, STATE_NAME;
quit;

/* 12. Standardizare pentru clustering */
proc standard data=work.airport_cluster_base
              mean=0 std=1
              out=work.airport_cluster_std;
    var mean_traffic mean_total_delay mean_delay_per_flight;
run;

/* 13. K-Means / FASTCLUS */
proc fastclus data=work.airport_cluster_std
              maxclusters=4
              maxiter=100
              out=proj.airport_clusters
              outstat=work.cluster_stats;
    var mean_traffic mean_total_delay mean_delay_per_flight;
    id APT_ICAO;
run;

/* 14. Reatasam valorile originale pentru interpretare */
proc sql;
    create table proj.airport_cluster_profile as
    select
        c.cluster,
        b.APT_ICAO,
        b.STATE_NAME,
        b.n_days,
        b.mean_traffic,
        b.mean_total_delay,
        b.mean_delay_per_flight,
        b.total_traffic,
        b.total_delay
    from proj.airport_clusters as c
    inner join work.airport_cluster_base as b
        on c.APT_ICAO = b.APT_ICAO
       and c.STATE_NAME = b.STATE_NAME;
quit;

/* 15. Rapoarte pentru clustering */
title "Distributia aeroporturilor pe clustere";
proc freq data=proj.airport_cluster_profile;
    tables cluster / nocum;
run;

title "Profilul clusterelor pe valori originale";
proc means data=proj.airport_cluster_profile n mean min max maxdec=3;
    class cluster;
    var mean_traffic mean_total_delay mean_delay_per_flight total_traffic total_delay;
run;

title "Primele 20 de aeroporturi clasificate pe clustere";
proc print data=proj.airport_cluster_profile(obs=20) noobs;
    var cluster APT_ICAO STATE_NAME mean_traffic mean_total_delay
        mean_delay_per_flight total_traffic total_delay;
run;

title;
ods graphics off;