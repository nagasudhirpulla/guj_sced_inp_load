-- DROP TABLE public.revs_info;

CREATE TABLE public.revs_info (
	id serial4 NOT NULL,
	rev_date timestamp NOT NULL,
	guj_rev int2 NOT NULL,
	rev_num int2 NOT NULL,
	rev_time timestamp NOT NULL,
	CONSTRAINT revs_info_un_guj_rev UNIQUE (rev_date, guj_rev),
	CONSTRAINT revs_info_un_rev UNIQUE (rev_date, rev_num)
);