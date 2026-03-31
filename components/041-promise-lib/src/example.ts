
import { MyPromise } from './index';

async function example() {
  console.log('--- Static Resolve/Reject ---');
  const p1 = MyPromise.resolve(1);
  const p2 = MyPromise.reject('error');

  p1.then(v => console.log('Resolved:', v));
  p2.catch(e => console.log('Rejected:', e));

  console.log('\n--- Promise.all ---');
  try {
    const all = await MyPromise.all([
      MyPromise.resolve(10),
      new MyPromise(resolve => setTimeout(() => resolve(20), 100)),
      30
    ]);
    console.log('Promise.all result:', all);
  } catch (e) {
    console.error(e);
  }

  console.log('\n--- Promise.any ---');
  try {
    const any = await MyPromise.any([
      MyPromise.reject('fail 1'),
      MyPromise.resolve('win'),
      MyPromise.reject('fail 2')
    ]);
    console.log('Promise.any result:', any);
  } catch (e) {
    console.error(e);
  }

  console.log('\n--- finally ---');
  MyPromise.resolve('test finally')
    .finally(() => console.log('Finally block executed'))
    .then(v => console.log('After finally:', v));
}

example();
