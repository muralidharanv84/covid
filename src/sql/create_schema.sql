--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: appointments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appointments (
    session_id character varying(256) NOT NULL,
    district_id integer NOT NULL,
    center_id integer NOT NULL,
    center_name character varying(256),
    pincode integer NOT NULL,
    fee_type character varying(256),
    date date NOT NULL,
    available_capacity integer NOT NULL,
    min_age integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    vaccine character varying(128)
);


ALTER TABLE public.appointments OWNER TO postgres;

--
-- Name: districts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.districts (
    id integer NOT NULL,
    state_id integer NOT NULL,
    name character varying(256),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.districts OWNER TO postgres;

--
-- Name: states; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.states (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    name character varying(256)
);


ALTER TABLE public.states OWNER TO postgres;

--
-- Name: districts districts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT districts_pkey PRIMARY KEY (id);


--
-- Name: states states_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.states
    ADD CONSTRAINT states_pkey PRIMARY KEY (id);


--
-- Name: distric_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX distric_id ON public.appointments USING btree (district_id);


--
-- Name: appointments district_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT district_id FOREIGN KEY (district_id) REFERENCES public.districts(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;


--
-- Name: districts states_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT states_fk FOREIGN KEY (state_id) REFERENCES public.states(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--
