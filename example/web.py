import djmicro
djmicro.configure()

from django.shortcuts import render

@djmicro.route(r'^$')
def hello(request):
    return render(request, 'index.html', {})

@djmicro.route(r'^test/(\d+)/$')
def test(request, id):
    return render(request, 'test.html', {'id': id})

if __name__ == '__main__':
    djmicro.run()