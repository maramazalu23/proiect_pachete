/* 02_build_final_dataset.sas */
/* Etapa 2: concatenare, curatare si construire FINAL_DATASET */

options validvarname=any;

%let root=/home/u64494277/pachete_software_sas;
libname proj "&root/sasdata";

/* 1. Curatare + concatenare trafic (intermediar in WORK) */
data work.traffic_clean;
    set proj.airport_traffic_2019
        proj.airport_traffic_2020
        proj.airport_traffic_2021
        proj.airport_traffic_2022
        proj.airport_traffic_2023;

    if missing(FLT_DATE) or missing(APT_ICAO) then delete;

    traffic = FLT_TOT_1;

    keep FLT_DATE APT_ICAO APT_NAME STATE_NAME traffic;
    format FLT_DATE yymmdd10.;
run;

/* 2. Curatare + concatenare intarzieri (intermediar in WORK) */
/* IMPORTANT:
   adunam doar cauzele specifice, NU folosim DLY_APT_ARR_:,
   pentru a evita includerea totalului DLY_APT_ARR_1 si dublarea valorilor
*/
data work.delays_clean;
    set proj.apt_dly_2019
        proj.apt_dly_2020
        proj.apt_dly_2021
        proj.apt_dly_2022
        proj.apt_dly_2023;

    flt_date_clean = datepart(FLT_DATE);
    format flt_date_clean yymmdd10.;

    if missing(APT_ICAO) or missing(flt_date_clean) then delete;

    array cause_vars {*} 
        DLY_APT_ARR_A_1
        DLY_APT_ARR_C_1
        DLY_APT_ARR_D_1
        DLY_APT_ARR_E_1
        DLY_APT_ARR_G_1
        DLY_APT_ARR_I_1
        DLY_APT_ARR_M_1
        DLY_APT_ARR_N_1
        DLY_APT_ARR_O_1
        DLY_APT_ARR_P_1
        DLY_APT_ARR_R_1
        DLY_APT_ARR_S_1
        DLY_APT_ARR_T_1
        DLY_APT_ARR_V_1
        DLY_APT_ARR_W_1
        DLY_APT_ARR_NA_1
    ;

    do i = 1 to dim(cause_vars);
        if missing(cause_vars[i]) then cause_vars[i] = 0;
    end;

    total_delay = sum(of cause_vars[*]);

    keep flt_date_clean APT_ICAO total_delay;
run;

/* 3. Construirea setului final direct prin PROC SQL */
/* agregam in subinterogari inainte de join, ca sa evitam dublari accidentale */
proc sql;
    create table proj.final_dataset as
    select
        t.FLT_DATE as FLT_DATE format=yymmdd10. label="Data zborului",
        t.APT_ICAO as APT_ICAO label="Cod ICAO aeroport",
        t.APT_NAME as APT_NAME label="Nume aeroport",
        t.STATE_NAME as STATE_NAME label="Tara",
        t.traffic as traffic label="Trafic total",
        coalesce(d.total_delay, 0) as total_delay label="Intarziere totala",
        year(t.FLT_DATE) as year label="An",
        month(t.FLT_DATE) as month label="Luna numerica",
        strip(put(t.FLT_DATE, monname.)) as month_name length=9 label="Numele lunii"
    from
        (
            select
                FLT_DATE,
                APT_ICAO,
                APT_NAME,
                STATE_NAME,
                sum(traffic) as traffic
            from work.traffic_clean
            group by FLT_DATE, APT_ICAO, APT_NAME, STATE_NAME
        ) as t
    left join
        (
            select
                flt_date_clean,
                APT_ICAO,
                sum(total_delay) as total_delay
            from work.delays_clean
            group by flt_date_clean, APT_ICAO
        ) as d
    on  t.FLT_DATE = d.flt_date_clean
    and t.APT_ICAO = d.APT_ICAO
    order by calculated year, calculated month, STATE_NAME, APT_ICAO, FLT_DATE
    ;
quit;

/* 4. Verificari */
title "Numar observatii - seturi intermediare si FINAL_DATASET";
proc sql;
    select "TRAFFIC_CLEAN" as Tabel length=20, count(*) as Observatii
    from work.traffic_clean

    union all

    select "DELAYS_CLEAN" as Tabel length=20, count(*) as Observatii
    from work.delays_clean

    union all

    select "FINAL_DATASET" as Tabel length=20, count(*) as Observatii
    from proj.final_dataset
    ;
quit;

title "Primele 10 observatii din FINAL_DATASET";
proc print data=proj.final_dataset(obs=10) noobs;
run;

title "Verificare rapida pentru TRAFFIC si TOTAL_DELAY";
proc means data=proj.final_dataset n nmiss min max mean;
    var traffic total_delay;
run;

title "Structura FINAL_DATASET";
proc contents data=proj.final_dataset varnum;
run;

title;

/* 5. Curatare WORK */
proc datasets lib=work nolist;
    delete traffic_clean delays_clean;
quit;