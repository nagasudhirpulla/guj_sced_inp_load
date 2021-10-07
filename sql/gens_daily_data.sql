-- public.gens_daily_data definition

-- Drop table

-- DROP TABLE public.gens_daily_data;

CREATE TABLE public.gens_daily_data (
	id serial NOT NULL,
	g_id int2 NOT NULL,
	data_type varchar(50) NOT NULL,
	data_date timestamp NOT NULL,
	data_val float4 NOT NULL,
	rev int2 NOT NULL,
	CONSTRAINT gens_daily_data_g_id_data_type_data_date_rev_key UNIQUE (g_id, data_type, data_date, rev),
	CONSTRAINT gens_daily_data_pkey PRIMARY KEY (id),
	CONSTRAINT gens_daily_data_rev_check CHECK (((rev >= 0) AND (rev <= 1000))),
	CONSTRAINT gens_daily_data_sch_type_check CHECK (((data_type)::text = ANY ((ARRAY['vc'::character varying, 'avg_pu_cap'::character varying, 'tm_pu'::character varying, 'rup_pu'::character varying, 'rdn_pu'::character varying])::text[])))
);


-- public.gens_daily_data foreign keys

ALTER TABLE public.gens_daily_data ADD CONSTRAINT gens_daily_data_g_id_fkey FOREIGN KEY (g_id) REFERENCES public.gens(id) ON DELETE RESTRICT ON UPDATE CASCADE;