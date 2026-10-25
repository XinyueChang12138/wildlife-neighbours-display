-- Run in a disposable database with migrations 001, 003, 004 and sample stories applied.
begin;
insert into auth.users(id,raw_user_meta_data) values('aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa','{"display_name":"Test resident"}'),('bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb','{"display_name":"Other resident"}'),('cccccccc-cccc-4ccc-cccc-cccccccccccc','{"display_name":"Test moderator"}');
insert into public.moderators values('cccccccc-cccc-4ccc-cccc-cccccccccccc','Test wildlife moderator');
select id as story from public.public_stories limit 1 \gset
set local role anon;
do $$begin
 begin perform public.create_direct_comment(gen_random_uuid(),'A quiet encounter.',null);raise exception 'Guest posted a comment';exception when insufficient_privilege then null;end;
end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa',true);
select public.create_direct_comment(:'story','A quiet encounter.',null) as posted \gset
select (:'posted'::jsonb->>'id') as cid \gset
select public.submit_observation('{"possibleSpecies":"not-sure","approximateTime":"Around dusk","publicArea":"General park area","privateRescueLocation":"PRIVATE RESCUE TEST LOCATION","behaviour":"Resting","description":"A possible animal rested in a tree.","injuryConcern":true}'::jsonb) as receipt \gset
select (:'receipt'::jsonb->>'id') as oid \gset
do $$declare own jsonb;begin own:=public.my_observations();if own::text like '%PRIVATE RESCUE TEST LOCATION%' or own::text like '%private_rescue_location%' then raise exception 'Private rescue location exposed in own profile';end if;end $$;
select public.edit_own_comment(:'cid','I watched from a distance.');
reset role;
set local role anon;
do $$begin if not exists(select 1 from public.comments where body='I watched from a distance.' and status='visible') then raise exception 'Comment not immediately public';end if;end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb',true);
-- Other residents must not edit someone else's visible comment.
select set_config('test.comment_id',:'cid',true);
do $$declare refused boolean:=false;begin
 begin perform public.edit_own_comment(current_setting('test.comment_id')::uuid,'Not mine');exception when others then refused:=true;end;
 if not refused then raise exception 'Another resident edited a comment';end if;
 if public.my_observations()<>'[]'::jsonb then raise exception 'Another resident sees private observations';end if;
end $$;
select public.report_direct_comment(:'cid','Other concern','Please check this demonstration discussion.');
reset role;
set local role anon;
do $$begin if not exists(select 1 from public.comments where body='I watched from a distance.') then raise exception 'Report incorrectly hid a comment';end if;end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','cccccccc-cccc-4ccc-cccc-cccccccccccc',true);
select public.moderate_direct_comment(:'cid','remove','Removed after a test review.');
reset role;
set local role anon;
do $$begin if exists(select 1 from public.comments where body='I watched from a distance.') then raise exception 'Removed comment publicly visible';end if;end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','cccccccc-cccc-4ccc-cccc-cccccccccccc',true);
select public.moderate_direct_comment(:'cid','restore','Restored after review.');
do $$begin if (select count(*) from public.comment_actions where comment_id=current_setting('test.comment_id')::uuid)<>2 then raise exception 'Comment actions not audited';end if;end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa',true);
select public.delete_own_comment(:'cid');
reset role;
set local role anon;
do $$begin if exists(select 1 from public.comments where body='I watched from a distance.') then raise exception 'Author deletion still visible';end if;end $$;
reset role;
rollback;
