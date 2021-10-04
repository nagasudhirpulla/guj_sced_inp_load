-- public.gens definition

-- Drop table

-- DROP TABLE public.gens;

CREATE TABLE public.gens (
	id smallserial NOT NULL,
	g_name varchar(250) NOT NULL,
	vc float4 NOT NULL,
	fuel_type varchar(100) NOT NULL,
	ins_cap float4 NOT NULL,
	avg_pu_cap float4 NOT NULL,
	tm_pu float4 NOT NULL,
	rup_pu float4 NOT NULL,
	rdn_pu float4 NOT NULL,
	CONSTRAINT gens_fuel_type_check CHECK (((fuel_type)::text = ANY (ARRAY[('coal'::character varying)::text, ('gas'::character varying)::text]))),
	CONSTRAINT gens_g_name_key UNIQUE (g_name),
	CONSTRAINT gens_pkey PRIMARY KEY (id),
	CONSTRAINT gens_vc_check CHECK ((vc >= (0)::double precision))
);