-- DROP TABLE public.daywise_latest_revs;

CREATE TABLE public.daywise_latest_revs (
	id serial4 NOT NULL,
	rev_date timestamp NOT NULL,
	latest_guj_rev int2 NOT NULL,
	latest_rev int2 NOT NULL,
	CONSTRAINT daywise_latest_revs_un_date UNIQUE (rev_date)
);