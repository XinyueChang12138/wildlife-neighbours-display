-- Additional tests for a disposable test database with the schema applied.
begin;
insert into auth.users(id) values('33333333-3333-4333-a333-333333333333');
insert into public.moderators values('33333333-3333-4333-a333-333333333333','Test outcome reviewer');
insert into opportunities(id,data) values('test-outcome-activity','{"status":"sample","registrationOpen":true}');
set local role anon;
insert into storage.objects(bucket_id,name) values('pending-media','44444444-4444-4444-a444-444444444444.jpg');
do $$begin
 if exists(select 1 from storage.objects where bucket_id='pending-media') then raise exception 'Pending media publicly readable';end if;
 begin
  insert into storage.objects(bucket_id,name) values('approved-media','44444444-4444-4444-a444-444444444444.jpg');
  raise exception 'Anon could write approved media';
 exception when insufficient_privilege then null;end;
end $$;
reset role;
set local role authenticated;
select set_config('request.jwt.claim.sub','33333333-3333-4333-a333-333333333333',true);
select public.publish_outcome('{"opportunityId":"test-outcome-activity","title":"Sample preparation","publicArea":"General park area","completedAt":"2026-01-01","actionsCompleted":"Sample litter collection","communityMessage":"No measured impact claim","sample":true}'::jsonb);
do $$begin
 if not exists(select 1 from storage.objects where bucket_id='pending-media') then raise exception 'Moderator cannot review media';end if;
 if not exists(select 1 from outcomes where opportunity_id='test-outcome-activity' and published) then raise exception 'Outcome not published';end if;
 if not exists(select 1 from opportunities where id='test-outcome-activity' and data->>'status'='completed' and data->>'registrationOpen'='false') then raise exception 'Activity not completed atomically';end if;
end $$;
reset role;
rollback;
