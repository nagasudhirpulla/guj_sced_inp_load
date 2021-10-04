-- public.gens_data definition

-- Drop table

-- DROP TABLE public.gens_data;

CREATE TABLE public.gens_data (
	id serial NOT NULL,
	g_id int2 NOT NULL,
	sch_type varchar(50) NOT NULL,
	sch_time timestamp NOT NULL,
	sch_val float4 NOT NULL,
	rev int2 NOT NULL,
	CONSTRAINT gens_data_g_id_sch_type_sch_time_rev_key UNIQUE (g_id, sch_type, sch_time, rev),
	CONSTRAINT gens_data_pkey PRIMARY KEY (id),
	CONSTRAINT gens_data_rev_check CHECK (((rev >= 0) AND (rev <= 1000))),
	CONSTRAINT gens_data_sch_type_check CHECK (((sch_type)::text = ANY (ARRAY[('sch'::character varying)::text, ('onbar'::character varying)::text, ('normbar'::character varying)::text, ('opt'::character varying)::text, ('tm'::character varying)::text, ('rup'::character varying)::text, ('rdn'::character varying)::text])))
);


-- public.gens_data foreign keys

ALTER TABLE public.gens_data ADD CONSTRAINT gens_data_g_id_fkey FOREIGN KEY (g_id) REFERENCES gens(id) ON UPDATE CASCADE ON DELETE RESTRICT;