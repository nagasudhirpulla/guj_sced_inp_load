CREATE TABLE public.smp_data (
	id serial4 NOT NULL,
	region_tag varchar(50) NOT NULL,
	data_time timestamp NOT NULL,
	smp_val float4 NOT NULL,
	rev int2 NOT NULL,
	CONSTRAINT smp_data_region_tag_data_time_rev_key UNIQUE (region_tag, data_time, rev),
	CONSTRAINT smp_data_pkey PRIMARY KEY (id),
	CONSTRAINT smp_data_rev_check CHECK (((rev >= 0) AND (rev <= 1000))),
	CONSTRAINT smp_data_region_tag_check CHECK (((region_tag)::text = ANY (ARRAY[('g'::character varying)::text])))
);