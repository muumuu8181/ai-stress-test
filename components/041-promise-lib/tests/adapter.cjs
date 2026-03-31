
const { MyPromise } = require('../dist/src/index');

exports.resolved = (value) => MyPromise.resolve(value);
exports.rejected = (reason) => MyPromise.reject(reason);
exports.deferred = () => {
  let resolve;
  let reject;
  const promise = new MyPromise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return {
    promise,
    resolve,
    reject,
  };
};
