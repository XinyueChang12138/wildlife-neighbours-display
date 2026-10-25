-- Run against a disposable database after applying the Supabase migration.
begin;
insert into auth.users(id) values('11111111-1111-1111-1111-111111111111');
insert into public.moderators values('11111111-1111-1111-1111-111111111111','Test wildlife reviewer');
set local role anon;
select public.submit_observation('{"possibleSpecies":"not-sure","approximateTime":"Around dusk","publicArea":"General park area","behaviour":"Resting","description":"A mystery animal rested in a tree.","injuryConcern":true,"privateRescueLocation":"PRIVATE TEST ADDRESS"}'::jsonb) as receipt \gset
reset role;
select (:'receipt'::jsonb->>'id') as oid \gset
set local role authenticated;
select set_config('request.jwt.claim.sub','11111111-1111-1111-1111-111111111111',true);
select public.moderate_observation(jsonb_build_object('id',:'oid','action','approve','reason','Privacy review completed','publicText','A possible animal rested in the park trees.','approvedSpecies','not-sure','approvedPublicArea','General park area','privacyChecks','{"face":true,"house":true,"plate":true,"location":true,"welfare":true}'::jsonb,'mediaApproved',false));
reset role;
set local role anon;
do $$ begin
 if exists(select 1 from public.public_stories where row_to_json(public_stories)::text like '%PRIVATE TEST ADDRESS%') then raise exception 'Private rescue location leaked';end if;
 if (select count(*) from public.public_stories)<>1 then raise exception 'Approval did not publish exactly one story';end if;
 begin
  perform * from public.observations;
  raise exception 'Anon read private observations';
 exception when insufficient_privilege then null;end;
 begin
  perform * from public.moderation_records;
  raise exception 'Anon read audit records';
 exception when insufficient_privilege then null;end;
 begin
  perform public.moderate_observation('{}');
  raise exception 'Anon moderation allowed';
 exception when insufficient_privilege then null;end;
end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','22222222-2222-2222-2222-222222222222',true);
do $$begin
 if exists(select 1 from public.observations) then raise exception 'Nonmoderator read private observations';end if;
 begin
  insert into public.public_stories(species,public_area,approximate_time,behaviour,story_text,verified_fact,fact_source,reviewed_by) values('not-sure','General park area','Around dusk','Resting','Unauthorised story','None','','Fake');
  raise exception 'Nonmoderator could publish';
 exception when insufficient_privilege then null;end;
end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','11111111-1111-1111-1111-111111111111',true);
select public.moderate_observation(jsonb_build_object('id',:'oid','action','reject','reason','Rejection test'));
reset role;
set local role anon;
do $$begin if exists(select 1 from public.public_stories) then raise exception 'Rejected story remains public';end if;end $$;
reset role;
rollback;
